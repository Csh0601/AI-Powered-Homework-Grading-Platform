import Slider from '@react-native-community/slider';
import React, { useState } from 'react';
import { Button, Image, StyleSheet, Text, View } from 'react-native';
import apiService from '../services/apiService';

interface ImageEditorProps {
  imageUri: string;
  onEditComplete?: (result: any) => void;
}

const ImageEditor: React.FC<ImageEditorProps> = ({ imageUri, onEditComplete }) => {
  const [rotation, setRotation] = useState(0);
  const [brightness, setBrightness] = useState(1);
  // 裁剪区域等可扩展

  // 这里只是演示，实际裁剪/亮度处理需用第三方库如 expo-image-manipulator
  const handleRotate = () => {
    setRotation((prev) => prev + 90);
  };

  const handleBrightnessChange = (value: number) => {
    setBrightness(value);
  };

  // 完成编辑，上传图片并回调
  const handleEditComplete = async () => {
    try {
      const file = {
        uri: imageUri,
        name: imageUri.split('/').pop() || 'image.jpg',
        type: 'image/jpeg',
      };
      const result = await apiService.uploadImage(file);
      if (onEditComplete) onEditComplete(result);
    } catch (e: any) {
      let msg = '图片上传或批改失败';
      if (typeof e === 'string') msg = e;
      else if (e && typeof e === 'object' && 'message' in e) msg = String((e as any).message);
      alert(msg);
    }
  };

  return (
    <View style={styles.container}>
      <Image
        source={{ uri: imageUri }}
        style={[
          styles.image,
          {
            transform: [{ rotate: `${rotation}deg` }],
            opacity: brightness, // 仅演示，实际应用滤镜
          },
        ]}
      />
      <View style={styles.controls}>
        <Button title="旋转90°" onPress={handleRotate} />
        <View style={styles.sliderRow}>
          <Text>亮度</Text>
          <Slider
            style={{ width: 150 }}
            minimumValue={0.2}
            maximumValue={2}
            value={brightness}
            onValueChange={handleBrightnessChange}
            step={0.01}
          />
        </View>
        {/* 裁剪功能可用第三方库实现，这里预留按钮 */}
        <Button title="完成编辑" onPress={handleEditComplete} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  image: {
    width: 250,
    height: 350,
    marginBottom: 20,
    backgroundColor: '#eee',
  },
  controls: {
    width: '100%',
    alignItems: 'center',
  },
  sliderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 10,
    gap: 10,
  },
});

export default ImageEditor; 