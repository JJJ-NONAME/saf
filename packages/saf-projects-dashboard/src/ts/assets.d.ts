declare module "*.svg" {
  const content: string;
  export default content;
}

declare module "*.css" {}

declare module "*.ttf" {
  const src: string;
  export default src;
}
