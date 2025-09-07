/// <reference types="vite/client" />
/// <reference types="react" />
/// <reference types="react-dom" />

declare module '*.svg' {
  const src: string;
  export default src;
}

declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

// React JSX support
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

// React module declarations
declare module 'react' {
  export * from 'react';
}

declare module 'react-router-dom' {
  export * from 'react-router-dom';
} 