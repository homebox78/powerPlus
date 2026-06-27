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

  const insert = useCallback(async (asset: Asset) => {
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
        return;
      }

      await PowerPoint.run(async (context) => {
        const selected = context.presentation.getSelectedSlides();
        selected.load("items");
        await context.sync();

        const slide =
          selected.items[0] ?? context.presentation.slides.getItemAt(0);

        const image = slide.shapes.addImage(base64);
        // 기본 크기/위치: 가로세로 150pt, 슬라이드 중앙 근처
        image.width = 150;
        image.height = 150;
        image.left = 285; // 표준 16:9(960pt 폭) 기준 대략 중앙
        image.top = 160;

        await context.sync();
      });

      setState({
        insertingId: null,
        message: `"${asset.name}" 삽입 완료`,
        error: false,
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setState({ insertingId: null, message: `삽입 실패: ${msg}`, error: true });
    }
  }, []);

  const clearMessage = useCallback(() => {
    setState((s) => ({ ...s, message: null, error: false }));
  }, []);

  return { ...state, insert, clearMessage };
}
