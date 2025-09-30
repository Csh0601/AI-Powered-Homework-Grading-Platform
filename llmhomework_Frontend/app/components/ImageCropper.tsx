// ImageCropper.tsx
import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  View,
  Image,
  StyleSheet,
  Dimensions,
  Text,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Animated,
  Alert,
} from 'react-native';
import {
  Gesture,
  GestureDetector,
  GestureHandlerRootView,
} from 'react-native-gesture-handler';
import { runOnJS } from 'react-native-reanimated';
import imageService from '../services/imageService';
import { DecorativeButton } from './DecorativeButton';

// 主题色（按需替换）
const primaryColor = '#007AFF';
const textColor = '#000000';
const secondaryTextColor = '#555555';
const cardBackgroundColor = '#FFFFFF';
const backgroundColor = '#F9F9F9';
const successColor = '#34C759';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface CropArea {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface ImageCropperProps {
  imageUri: string;
  onCropComplete: (croppedUri: string) => void;
  onCancel: () => void;
}

const MIN_CROP_SIZE = 50; // 最小裁剪边长（像素，显示坐标系）

const ImageCropper: React.FC<ImageCropperProps> = ({
  imageUri,
  onCropComplete,
  onCancel,
}) => {
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 }); // 原始图片像素
  const [displaySize, setDisplaySize] = useState({ width: 0, height: 0 }); // 在屏幕上的显示尺寸（px）
  const [cropArea, setCropArea] = useState<CropArea>({
    x: 50,
    y: 50,
    width: 200,
    height: 200,
  });
  const [isProcessing, setIsProcessing] = useState(false);

  // refs 用于在 worklet/手势开始时保存初始值
  const cropRef = useRef<CropArea>(cropArea);
  const savedCropRef = useRef<CropArea>(cropArea);

  // 用于记录移动开始的基准位移
  const savedTranslateX = useRef(0);
  const savedTranslateY = useRef(0);

  // 动画
  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(50));
  const [scaleAnim] = useState(new Animated.Value(0.96));

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 450, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 450, useNativeDriver: true }),
      Animated.spring(scaleAnim, { toValue: 1, friction: 7, tension: 50, useNativeDriver: true }),
    ]).start();
  }, []);

  // Keep ref in sync
  useEffect(() => {
    cropRef.current = cropArea;
  }, [cropArea]);

  // 组件卸载时清理手势状态
  useEffect(() => {
    return () => {
      console.log('✂️ ImageCropper组件卸载，清理手势状态');
      // 强制清理手势状态，防止影响其他手势处理
    };
  }, []);

  // 获取原始图片尺寸并计算显示尺寸（保持等比，按屏幕宽度展示）
  useEffect(() => {
    if (!imageUri) return;
    Image.getSize(
      imageUri,
      (w, h) => {
        setImageSize({ width: w, height: h });
        const containerW = screenWidth - 40; // 两侧 margin 20
        const ratio = w / h;
        let displayW = containerW;
        let displayH = displayW / ratio;
        // 限制最大高度不超过屏幕的60%（可调整）
        const maxH = screenHeight * 0.56;
        if (displayH > maxH) {
          displayH = maxH;
          displayW = displayH * ratio;
        }
        setDisplaySize({ width: displayW, height: displayH });

        // 初始裁剪区域：尽可能覆盖图片中心，可为长方形（以图片显示比例为基线）
        const initialW = Math.min(displayW * 0.8, displayW);
        const initialH = Math.min(displayH * 0.6, displayH);
        const initialX = Math.max(0, (displayW - initialW) / 2);
        const initialY = Math.max(0, (displayH - initialH) / 2);
        const initial: CropArea = {
          x: initialX,
          y: initialY,
          width: initialW,
          height: initialH,
        };
        setCropArea(initial);
        savedCropRef.current = initial;
      },
      (err) => {
        console.error('Image.getSize failed', err);
        Alert.alert('图片打开失败', '无法获取图片尺寸，请重试或使用其他图片。');
      }
    );
  }, [imageUri]);

  // 辅助：限制区间
  const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));

  // ========== JS handlers（runOnJS 会调用这些函数） ==========
  // 开始移动（记录起始基准）
  const startMove = useCallback(() => {
    savedTranslateX.current = cropRef.current.x;
    savedTranslateY.current = cropRef.current.y;
  }, []);

  // 执行移动（dx, dy 是从手势传来的 translation）
  const handleMove = useCallback((dx: number, dy: number) => {
    const savedX = savedTranslateX.current;
    const savedY = savedTranslateY.current;
    const w = displaySize.width;
    const h = displaySize.height;
    const cur = cropRef.current;
    const newX = clamp(savedX + dx, 0, Math.max(0, w - cur.width));
    const newY = clamp(savedY + dy, 0, Math.max(0, h - cur.height));
    setCropArea(prev => ({ ...prev, x: newX, y: newY }));
  }, [displaySize.width, displaySize.height]);

  // 开始缩放（记录基准）
  const startPinch = useCallback(() => {
    savedCropRef.current = { ...cropRef.current };
  }, []);

  // 缩放（以裁剪框中心为基点，scale 是相对于开始手势的倍数）
  const handlePinch = useCallback((scale: number) => {
    const saved = savedCropRef.current;
    if (!saved || !displaySize.width || !displaySize.height) return;
    const baseW = saved.width;
    const baseH = saved.height;
    let newW = clamp(baseW * scale, MIN_CROP_SIZE, displaySize.width);
    let newH = clamp(baseH * scale, MIN_CROP_SIZE, displaySize.height);
    // 防止超出显示边界
    newW = Math.min(newW, displaySize.width);
    newH = Math.min(newH, displaySize.height);
    const centerX = saved.x + baseW / 2;
    const centerY = saved.y + baseH / 2;
    let newX = centerX - newW / 2;
    let newY = centerY - newH / 2;
    newX = clamp(newX, 0, displaySize.width - newW);
    newY = clamp(newY, 0, displaySize.height - newH);
    setCropArea({ x: newX, y: newY, width: newW, height: newH });
  }, [displaySize.width, displaySize.height]);

  // 开始角点缩放（记录基准）
  const startResize = useCallback((corner: string) => {
    savedCropRef.current = { ...cropRef.current };
  }, []);

  // 角点缩放处理：corner = 'tl'|'tr'|'bl'|'br'
  const handleResize = useCallback((corner: string, dx: number, dy: number) => {
    const saved = savedCropRef.current;
    if (!saved) return;
    const maxW = displaySize.width;
    const maxH = displaySize.height;
    let newX = saved.x, newY = saved.y, newW = saved.width, newH = saved.height;

    if (corner === 'tl') {
      // 左上角：移动 left/top，width/height 减少
      const left = clamp(saved.x + dx, 0, saved.x + saved.width - MIN_CROP_SIZE);
      const top = clamp(saved.y + dy, 0, saved.y + saved.height - MIN_CROP_SIZE);
      newX = left;
      newY = top;
      newW = saved.x + saved.width - left;
      newH = saved.y + saved.height - top;
    } else if (corner === 'tr') {
      // 右上角：改变 width（向右/左拖动）和 top
      const widthCandidate = clamp(saved.width + dx, MIN_CROP_SIZE, maxW - saved.x);
      const top = clamp(saved.y + dy, 0, saved.y + saved.height - MIN_CROP_SIZE);
      newW = widthCandidate;
      newY = top;
      newH = saved.y + saved.height - top;
    } else if (corner === 'bl') {
      // 左下角：改变 left 和 height
      const left = clamp(saved.x + dx, 0, saved.x + saved.width - MIN_CROP_SIZE);
      const heightCandidate = clamp(saved.height + dy, MIN_CROP_SIZE, maxH - saved.y);
      newX = left;
      newW = saved.x + saved.width - left;
      newH = heightCandidate;
    } else if (corner === 'br') {
      // 右下角：改变 width 和 height（右下正常拉伸）
      const widthCandidate = clamp(saved.width + dx, MIN_CROP_SIZE, maxW - saved.x);
      const heightCandidate = clamp(saved.height + dy, MIN_CROP_SIZE, maxH - saved.y);
      newW = widthCandidate;
      newH = heightCandidate;
    }

    // 再二次校准 x,y，避免越界
    newX = clamp(newX, 0, Math.max(0, displaySize.width - newW));
    newY = clamp(newY, 0, Math.max(0, displaySize.height - newH));

    setCropArea({ x: newX, y: newY, width: newW, height: newH });
  }, [displaySize.width, displaySize.height]);

  // ========== 手势创建 ==========
  // 移动 + 缩放（作用在整个裁剪框区域）
  const moveGesture = Gesture.Pan()
    .onBegin(() => {
      runOnJS(startMove)();
    })
    .onUpdate((e) => {
      runOnJS(handleMove)(e.translationX, e.translationY);
    });

  const pinchGesture = Gesture.Pinch()
    .onBegin(() => runOnJS(startPinch)())
    .onUpdate((e) => {
      // event.scale 是相对于手势开始的比例 (>0)
      // 忽略太小的变动以减少抖动
      if (Math.abs(e.scale - 1) < 0.01) return;
      runOnJS(handlePinch)(e.scale);
    });

  const moveAndPinch = Gesture.Simultaneous(pinchGesture, moveGesture);

  // 四个角的独立拖拽手势（每个 handle 一个 pan）
  const createCornerGesture = (corner: string) =>
    Gesture.Pan()
      .onBegin(() => runOnJS(startResize)(corner))
      .onUpdate((e) => {
        // translation 是相对于开始手势
        runOnJS(handleResize)(corner, e.translationX, e.translationY);
      });

  const panTL = createCornerGesture('tl');
  const panTR = createCornerGesture('tr');
  const panBL = createCornerGesture('bl');
  const panBR = createCornerGesture('br');

  // ========== 裁剪执行 ==========
  const handleCrop = async () => {
    if (isProcessing) return;
    try {
      setIsProcessing(true);
      if (!displaySize.width || !displaySize.height || !imageSize.width || !imageSize.height) {
        throw new Error('图片尺寸未就绪');
      }

      // 将显示坐标换算为原始像素坐标
      const scaleX = imageSize.width / displaySize.width;
      const scaleY = imageSize.height / displaySize.height;

      const cfg = {
        originX: Math.round(clamp(cropArea.x * scaleX, 0, imageSize.width - 1)),
        originY: Math.round(clamp(cropArea.y * scaleY, 0, imageSize.height - 1)),
        width: Math.round(clamp(cropArea.width * scaleX, 1, imageSize.width)),
        height: Math.round(clamp(cropArea.height * scaleY, 1, imageSize.height)),
      };

      // 边界校验
      if (cfg.width <= 0 || cfg.height <= 0) throw new Error('裁剪区域太小');
      if (cfg.originX + cfg.width > imageSize.width) cfg.width = imageSize.width - cfg.originX;
      if (cfg.originY + cfg.height > imageSize.height) cfg.height = imageSize.height - cfg.originY;

      // 调用 imageService （你需要确保该方法接受上述原始像素坐标）
      const resultUri = await imageService.cropImage(imageUri, cfg);
      onCropComplete(resultUri);
    } catch (err: any) {
      console.error('crop failed', err);
      Alert.alert('裁剪失败', err?.message ?? '未知错误');
    } finally {
      setIsProcessing(false);
    }
  };

  // ========== 布局计算（用来将 imageWrapper 居中） ==========
  const imageWrapperLeft = (screenWidth - displaySize.width) / 2; // 居中水平偏移（用于定位蒙层）
  // 注意：我们不使用 focal 点做缩放，缩放围绕裁剪框中心

  // ====== render ======
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="dark-content" backgroundColor={backgroundColor} />
        <Animated.View
          style={[
            styles.container,
            { opacity: fadeAnim, transform: [{ translateY: slideAnim }, { scale: scaleAnim }] },
          ]}
        >
          {/* header */}
          <View style={styles.header}>
            <DecorativeButton
              onPress={onCancel}
              iconName="close"
              size="sm"
              gradientColors={['#FF3B30', '#FF6B35']}
              outerColor="#FF9F0A"
              borderColor="#FF6B00"
            />

            <Text style={styles.headerTitle}>裁剪图片</Text>

            <DecorativeButton
              onPress={handleCrop}
              iconName="checkmark"
              size="sm"
              disabled={isProcessing}
              gradientColors={['#34C759', '#30D158']}
              outerColor="#A3F3BE"
              borderColor="#00C851"
            />
          </View>

          {/* 图片区域（居中） */}
          <View style={styles.imageContainer}>
            <GestureDetector gesture={moveAndPinch}>
              <View style={styles.gestureContainer}>
                <View
                  style={[
                    styles.imageWrapper,
                    { width: displaySize.width, height: displaySize.height },
                  ]}
                >
                  <Image source={{ uri: imageUri }} style={styles.image} resizeMode="contain" />

                  {/* 裁剪框（主体，可拖动） */}
                  <GestureDetector gesture={Gesture.Simultaneous(panTL, panTR, panBL, panBR, moveGesture)}>
                    <View
                      style={[
                        styles.cropFrame,
                        {
                          left: cropArea.x,
                          top: cropArea.y,
                          width: cropArea.width,
                          height: cropArea.height,
                        },
                      ]}
                    >
                      {/* 四个角的可拖拽手柄 */}
                      <GestureDetector gesture={panTL}>
                        <View style={[styles.handle, styles.handleTL]} />
                      </GestureDetector>

                      <GestureDetector gesture={panTR}>
                        <View style={[styles.handle, styles.handleTR]} />
                      </GestureDetector>

                      <GestureDetector gesture={panBL}>
                        <View style={[styles.handle, styles.handleBL]} />
                      </GestureDetector>

                      <GestureDetector gesture={panBR}>
                        <View style={[styles.handle, styles.handleBR]} />
                      </GestureDetector>
                    </View>
                  </GestureDetector>

                  {/* 半透明遮罩：使用 displaySize 计算 mask */}
                  <View style={[styles.overlay, { width: displaySize.width, height: displaySize.height }]}>
                    {/* top */}
                    <View style={[styles.mask, { left: 0, top: 0, right: 0, height: cropArea.y }]} />
                    {/* middle row */}
                    <View style={[styles.maskRow, { top: cropArea.y, height: cropArea.height }]}>
                      <View style={[styles.mask, { left: 0, width: cropArea.x }]} />
                      <View style={styles.transparentCropArea} />
                      <View style={[styles.mask, { right: 0, width: Math.max(0, displaySize.width - cropArea.x - cropArea.width) }]} />
                    </View>
                    {/* bottom */}
                    <View style={[styles.mask, { left: 0, bottom: 0, right: 0, height: Math.max(0, displaySize.height - cropArea.y - cropArea.height) }]} />
                  </View>
                </View>
              </View>
            </GestureDetector>
          </View>

          {/* 信息区 */}
          <View style={styles.infoContainer}>
            <Text style={styles.infoText}>
              尺寸：{Math.round(cropArea.width)} × {Math.round(cropArea.height)}（显示像素）
            </Text>
            <Text style={styles.infoText}>
              位置：({Math.round(cropArea.x)}, {Math.round(cropArea.y)})
            </Text>
          </View>

          {/* 提示 */}
          <View style={styles.tipContainer}>
            <Text style={styles.tipText}>拖动框体移动裁剪区域；拖动四角手柄独立改变宽高；双指缩放以裁剪框中心为基点放大/缩小。</Text>
          </View>
        </Animated.View>
      </SafeAreaView>
    </GestureHandlerRootView>
  );
};

export default ImageCropper;

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: backgroundColor },
  container: { flex: 1 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  cancelButton: { padding: 8 },
  cancelButtonText: { color: '#FF3B30', fontSize: 16 },
  headerTitle: { fontSize: 18, fontWeight: '700', color: textColor },
  confirmButton: {
    backgroundColor: successColor,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  confirmButtonText: { color: '#fff', fontSize: 16 },
  imageContainer: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  gestureContainer: { position: 'relative' },
  imageWrapper: {
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: cardBackgroundColor,
  },
  image: { width: '100%', height: '100%' },
  cropFrame: {
    position: 'absolute',
    borderWidth: 2,
    borderColor: primaryColor,
    backgroundColor: 'rgba(0,0,0,0.0)',
  },
  handle: {
    position: 'absolute',
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: primaryColor,
    borderWidth: 2,
    borderColor: '#fff',
    elevation: 6,
  },
  handleTL: { left: -11, top: -11 },
  handleTR: { right: -11, top: -11 },
  handleBL: { left: -11, bottom: -11 },
  handleBR: { right: -11, bottom: -11 },
  overlay: { position: 'absolute', left: 0, top: 0 },
  mask: { position: 'absolute', backgroundColor: 'rgba(0,0,0,0.45)' },
  maskRow: { position: 'absolute', left: 0, right: 0 },
  transparentCropArea: { flex: 1, backgroundColor: 'transparent' },
  infoContainer: {
    alignSelf: 'center',
    marginTop: 8,
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  infoText: { color: '#fff', fontSize: 12, textAlign: 'center' },
  tipContainer: { padding: 16 },
  tipText: { color: secondaryTextColor, textAlign: 'center' },
});
