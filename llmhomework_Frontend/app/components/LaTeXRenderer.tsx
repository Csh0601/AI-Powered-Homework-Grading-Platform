import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import { WebView } from 'react-native-webview';

interface LaTeXRendererProps {
  content: string;
  style?: any;
  fontSize?: number;
  color?: string;
}

const LaTeXRenderer: React.FC<LaTeXRendererProps> = ({ 
  content, 
  style, 
  fontSize = 16, 
  color = '#000' 
}) => {
  // 清理和转换LaTeX内容
  const cleanLaTeX = (text: string): string => {
    if (!text) return '';
    
    // 移除多余的反斜杠
    let cleaned = text.replace(/\\\\/g, '\\');
    
    // 确保分数格式正确
    cleaned = cleaned.replace(/\\frac\{(\d+)\}\{(\d+)\}/g, '\\frac{$1}{$2}');
    
    // 确保次方格式正确
    cleaned = cleaned.replace(/\^(\d+)/g, '^{$1}');
    
    // 处理负号
    cleaned = cleaned.replace(/\\times/g, '\\times');
    
    return cleaned;
  };

  const cleanedContent = cleanLaTeX(content);

  // 创建包含MathJax的HTML
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
      <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
      <script>
        window.MathJax = {
          tex: {
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
            processEscapes: true,
            processEnvironments: true
          },
          options: {
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process'
          },
          startup: {
            ready: () => {
              MathJax.startup.defaultReady();
              // 渲染完成后调整高度
              setTimeout(() => {
                const height = document.body.scrollHeight;
                window.ReactNativeWebView && window.ReactNativeWebView.postMessage(JSON.stringify({
                  type: 'resize',
                  height: height
                }));
              }, 100);
            }
          }
        };
      </script>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          font-size: ${fontSize}px;
          color: ${color};
          margin: 8px;
          padding: 0;
          line-height: 1.4;
          background: transparent;
        }
        .math-content {
          display: inline-block;
          vertical-align: middle;
        }
        .mjx-container {
          display: inline-block !important;
          margin: 0 !important;
        }
      </style>
    </head>
    <body>
      <div class="math-content">$${cleanedContent}$</div>
    </body>
    </html>
  `;

  const [webViewHeight, setWebViewHeight] = React.useState(fontSize * 2);

  const onMessage = (event: any) => {
    try {
      const data = JSON.parse(event.nativeEvent.data);
      if (data.type === 'resize' && data.height) {
        setWebViewHeight(Math.max(data.height, fontSize * 1.5));
      }
    } catch (e) {
      // 忽略非JSON消息
    }
  };

  return (
    <View style={[styles.container, style]}>
      <WebView
        source={{ html: htmlContent }}
        style={[styles.webview, { height: webViewHeight }]}
        scrollEnabled={false}
        showsVerticalScrollIndicator={false}
        showsHorizontalScrollIndicator={false}
        onMessage={onMessage}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={false}
        mixedContentMode="compatibility"
        allowsInlineMediaPlayback={true}
        mediaPlaybackRequiresUserAction={false}
        originWhitelist={['*']}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'transparent',
  },
  webview: {
    backgroundColor: 'transparent',
    flex: 0,
  },
});

export default LaTeXRenderer;
