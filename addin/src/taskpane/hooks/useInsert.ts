/* global PowerPoint, Office, Image, document, window */
import { useCallback, useState } from "react";
import type { Asset } from "../data/mockAssets";

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
  const res = await fetch(url);
  if (!res.ok) throw new Error("이미지 로드 실패");
  const blob = await res.blob();
  return await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1]);
    reader.onerror = () => reject(new Error("이미지 변환 실패"));
    reader.readAsDataURL(blob);
  });
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

  /** 자산을 현재 슬라이드에 삽입. 성공하면 true (최근 사용 기록용). sizePt 는 가로세로 크기(pt). */
  const insert = useCallback(async (asset: Asset, sizePt = 150): Promise<boolean> => {
    setState({ insertingId: asset.id, message: null, error: false });
    try {
      // 업로드 자산이면 이미지 URL을, 구 mock이면 SVG를 base64(PNG)로 변환
      const base64 = asset.image_url
        ? await imageUrlToBase64(asset.image_url)
        : await svgToPngBase64(asset.svg || "");

      if (!isPowerPoint()) {
        // 브라우저에서 미리보기 중 — 삽입은 PowerPoint에서만 가능
        setState({
          insertingId: null,
          message: "PowerPoint에서 열면 슬라이드에 삽입됩니다 (현재는 미리보기).",
          error: true,
        });
        return false;
      }

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
      await new Promise<void>((resolve, reject) => {
        const opts: Office.SetSelectedDataOptions & {
          imageWidth?: number;
          imageHeight?: number;
          imageLeft?: number;
          imageTop?: number;
        } = {
          coercionType: Office.CoercionType.Image,
          imageWidth: sizePt, // 단위 pt
          imageHeight: sizePt,
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
        message: `"${asset.name || asset.tags?.[0] || asset.id}" 삽입 완료`,
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
