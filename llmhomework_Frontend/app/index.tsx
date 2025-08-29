import React from 'react';
// import { Provider } from 'react-redux'; // 如用 Redux，可取消注释
// import store from './store'; // Redux store 预留
// import { AppContextProvider } from './context/AppContext'; // Context 预留
import AppNavigator from './navigation/AppNavigator';

export default function App() {
  return <AppNavigator />;
}

// 本文件为拍照实现大模型作业批改 App 的入口，已预留状态管理结构。 