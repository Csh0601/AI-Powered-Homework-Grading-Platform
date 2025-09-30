module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      // react-native-worklets/plugin 必须是最后一个插件
      'react-native-worklets/plugin',
    ],
  };
};
