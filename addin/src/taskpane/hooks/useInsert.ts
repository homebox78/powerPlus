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
      const base64 = await svgToPngBase64(asset.svg);

      if (!isPowerPoint()) {
        // 브라우저에서 미리보기 중 — 삽입은 PowerPoint에서만 가능
        setState({
          insertingId: null,
          message: "PowerPoint에서 열면 슬라이드에 삽입됩니다 (현재는 미리보기).",
          error: true,
        });
        return false;
      }

      await PowerPoint.run(async (context) => {
        const selected = context.presentation.getSelectedSlides();
        selected.load("items");
        await context.sync();

        const slide =
          selected.items[0] ?? context.presentation.slides.getItemAt(0);

        const image = slide.shapes.addImage(base64);
        // 표준 16:9 슬라이드(960×540pt)의 중앙에 sizePt 크기로 배치
        image.width = sizePt;
        image.height = sizePt;
        image.left = (960 - sizePt) / 2;
        image.top = (540 - sizePt) / 2;

        await context.sync();
      });

      setState({
        insertingId: null,
        message: `"${asset.name}" 삽입 완료`,
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
