// PowerPoint.ShapeCollection.addImage 는 런타임에는 동작하지만
// @types/office-js(1.0.593)의 PowerPoint 네임스페이스 선언에는 누락돼 있다
// (Excel 쪽에만 선언됨). 런타임 검증된 API 이므로 타입만 보강한다.
// 참고: hooks/useInsert.ts 의 slide.shapes.addImage 사용처.
declare namespace PowerPoint {
  interface ShapeCollection {
    addImage(base64ImageString: string, options?: PowerPoint.ShapeAddOptions): PowerPoint.Shape;
  }
}
