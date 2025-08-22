import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, info: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught:', error, info)
    this.setState({ info })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24 }}>
          <h1>Ocorreu um erro na aplicação.</h1>
          <p>Tente recarregar a página. Se persistir, envie o erro abaixo.</p>
          <pre style={{ whiteSpace: 'pre-wrap' }}>
            {String(this.state.error)}
            {'\n'}
            {this.state.info?.componentStack}
          </pre>
        </div>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
