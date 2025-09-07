import React, { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', border: '1px solid red', margin: '1rem', borderRadius: '8px', backgroundColor: '#fff5f5' }}>
          <h1>Что-то пошло не так.</h1>
          <p>Произошла ошибка при отображении этой части страницы.</p>
          {this.state.error && (
            <pre style={{ whiteSpace: 'pre-wrap', background: '#f0f0f0', padding: '1rem', borderRadius: '4px' }}>
              {this.state.error.toString()}
            </pre>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 