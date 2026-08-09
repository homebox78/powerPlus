/* global PowerPoint, Office, Image, document, window */
import { useCallback, useState } from "react";
import type { Asset } from "../data/mockAssets";
import { getToken } from "../api/auth";

/** SVG 문자열을 PNG base64(헤더 제외)로 변환.
 *  PowerPoint addImage()는 base64 인코딩된 PNG/JPEG를 받으므로
 *  벡터(SVG)를 canvas에 그려 래스터화한다. size는 출력 픽셀 해상도. */
function svgToPngBase64(svg: string, size = 512): Promise<string> {
  return new Promise((resolve, reject) => {
    const svgBlob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);
    const img = new Image();
    img.onload = () => {
      try {
        const canvas = document.createElement("canvas");
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("canvas 2d context 생성 실패");
        ctx.drawImage(img, 0, 0, size, size);
        const dataUrl = canvas.toDataURL("image/png");
        URL.revokeObjectURL(url);
        resolve(dataUrl.split(",")[1]); // "data:image/png;base64," 제거
      } catch (e) {
        URL.revokeObjectURL(url);
        reject(e);
      }
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("SVG 이미지 로드 실패"));
    };
    img.src = url;
  });
}

/** 서버 업로드 이미지(PNG/JPG) URL → base64(헤더 제외). Office addImage 는 PNG/JPEG base64 를 받는다. */
async function imageUrlToBase64(url: string): Promise<string> {
  // 이미지 프록시(/api/imageproxy)는 로그인 필요 → 토큰 동봉.
  // 단 **자사 출처일 때만** — image_url이 외부 호스트로 확장돼도 토큰이 새지 않게 가드.
  let sameOrigin = true;
  try {
    sameOrigin = new URL(url, window.location.href).origin === window.location.origin;
  } catch { sameOrigin = false; }
  const token = sameOrigin ? getToken() : null;
  const res = await fetch(url, token ? { headers: { Authorization: `Bearer ${token}` } } : undefined);
  if (!res.ok) throw new Error("이미지 로드 실패");
  const blob = await res.blob();
  return await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1]);
    reader.onerror = () => reject(new Error("이미지 변환 실패"));
    reader.readAsDataURL(blob);
  });
}

/** 장표(pptx base64)를 선택한 슬라이드 뒤에 삽입. 선택이 없으면 맨 끝에. (실패 시 기본 위치로 폴백) */
async function insertSlidesAfterSelection(base64: string): Promise<void> {
  const run = (useTarget: boolean) =>
    PowerPoint.run(async (context) => {
      const pres = context.presentation;
      const opts: PowerPoint.InsertSlideOptions = { formatting: "KeepSourceFormatting" };
      if (useTarget) {
        const sel = pres.getSelectedSlides();
        sel.load("items/id");
        const all = pres.slides;
        all.load("items/id");
        await context.sync();
        const id = sel.items.length
          ? sel.items[sel.items.length - 1].id // 선택한(마지막) 슬라이드 뒤
          : all.items.length
            ? all.items[all.items.length - 1].id // 선택 없으면 맨 끝
            : undefined;
        if (id) opts.targetSlideId = id;
      }
      pres.insertSlidesFromBase64(base64, opts);
      await context.sync();
    });
  // targetSlideId 형식 문제(SlideNotFound) 등 → 타겟 없이 재시도
  try {
    await run(true);
  } catch {
    await run(false);
  }
}

const isPowerPoint = (): boolean =>
  typeof Office !== "undefined" &&
  Office.context?.host === Office.HostType.PowerPoint;

export interface InsertState {
  insertingId: string | null;
  message: string | null;
  error: boolean;
}

export function useInsert() {
  const [state, setState] = useState<InsertState>({
    insertingId: null,
    message: null,
    error: false,
  });

  /** 자산을 현재 슬라이드에 삽입. 성공하면 true (최근 사용 기록용). 크기는 원본대로(사용자가 이후 조절). */
  const insert = useCallback(async (asset: Asset): Promise<boolean> => {
    setState({ insertingId: asset.id, message: null, error: false });
    const label = asset.name || asset.tags?.[0] || asset.id;
    try {
      if (!isPowerPoint()) {
        // 브라우저에서 미리보기 중 — 삽입은 PowerPoint에서만 가능
        setState({
          insertingId: null,
          message: "PowerPoint에서 열면 슬라이드에 삽입됩니다 (현재는 미리보기).",
          error: true,
        });
        return false;
      }

      // 장표(ppt) 자산 → 새 슬라이드로 추가 (이미지가 아니라 슬라이드 삽입)
      if (asset.slide_url) {
        const pptxB64 = await imageUrlToBase64(asset.slide_url); // 임의 바이너리 → base64
        await insertSlidesAfterSelection(pptxB64); // 선택 슬라이드 뒤(없으면 끝)에 추가
        setState({ insertingId: null, message: `"${label}" 장표 추가됨`, error: false });
        return true;
      }

      // 이미지 자산 → base64(PNG)로 변환
      const base64 = asset.image_url
        ? await imageUrlToBase64(asset.image_url)
        : await svgToPngBase64(asset.svg || "");

      // 슬라이드에서 선택한 개체가 있으면 그 위치에, 없으면 슬라이드 중앙에 삽입.
      // (Office 애드인 API는 마우스 포인터 픽셀 위치를 제공하지 않으므로 "선택 위치" 기준이 최선)
      let pos: { left: number; top: number } | null = null;
      try {
        await PowerPoint.run(async (context) => {
          const sel = context.presentation.getSelectedShapes();
          sel.load("items/left, items/top");
          await context.sync();
          if (sel.items.length > 0) {
            pos = { left: sel.items[0].left, top: sel.items[0].top };
          }
        });
      } catch {
        // getSelectedShapes 미지원/선택 없음 → 중앙 삽입으로 폴백
      }

      // 현재 슬라이드에 이미지 삽입 (Common API — 모든 PowerPoint 버전에서 동작).
      // 가로 기준 합리적 기본 크기로 삽입(세로는 비율 자동) → 원본이 너무 커서
      // 슬라이드를 벗어나는 일 방지. 이후 사용자가 자유롭게 조절.
      const DEFAULT_WIDTH_PT = 200;
      await new Promise<void>((resolve, reject) => {
        const opts: Office.SetSelectedDataOptions & {
          imageWidth?: number;
          imageLeft?: number;
          imageTop?: number;
        } = {
          coercionType: Office.CoercionType.Image,
          imageWidth: DEFAULT_WIDTH_PT, // 세로는 비율 유지로 자동 계산
        };
        if (pos) {
          opts.imageLeft = pos.left; // 선택한 개체 위치에 삽입
          opts.imageTop = pos.top;
        }
        Office.context.document.setSelectedDataAsync(base64, opts, (res) => {
          if (res.status === Office.AsyncResultStatus.Succeeded) resolve();
          else reject(new Error(res.error?.message || "삽입에 실패했습니다."));
        });
      });

      setState({
        insertingId: null,
        message: `"${label}" 삽입 완료`,
        error: false,
      });
      return true;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setState({ insertingId: null, message: `삽입 실패: ${msg}`, error: true });
      return false;
    }
  }, []);

  const clearMessage = useCallback(() => {
    setState((s) => ({ ...s, message: null, error: false }));
  }, []);

  return { ...state, insert, clearMessage };
}
