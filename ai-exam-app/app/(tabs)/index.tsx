import React, { useState } from 'react';
import { View, Button, Image, TextInput, Text, ScrollView } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';
import * as ImageManipulator from 'expo-image-manipulator';

export default function HomeScreen() {
  const [image, setImage] = useState<string | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [answers, setAnswers] = useState<string[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [wrongs, setWrongs] = useState<any[]>([]);
  const [genQ, setGenQ] = useState<string>('');

  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images, // 兼容老版本
      allowsEditing: true,
      quality: 1,
      exif: true, // 获取EXIF信息
    });
    // 新版API返回 result.canceled 和 result.assets
    if (!result.canceled && result.assets && result.assets.length > 0) {
      // 用ImageManipulator重新保存一份，自动修正方向
      const fixed = await ImageManipulator.manipulateAsync(
        result.assets[0].uri,
        [{ rotate: 0 }], // 旋转角度，0表示不旋转
        { compress: 0.8, format: ImageManipulator.SaveFormat.JPEG }
      );
      setImage(fixed.uri);
      alert('图片路径: ' + fixed.uri);
    }
  };

  const uploadImage = async () => {
    if (!image) {
      alert('没有图片');
      return;
    }
    alert('开始上传');
    let formData = new FormData();
    formData.append('image', {
      uri: image,
      name: 'photo.jpg',
      type: 'image/jpeg',
    } as any);
    formData.append('username', 'test');
    try {
      alert('即将发送请求');
      let res = await axios.post('http://192.168.10.239:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      alert('上传成功');
      setQuestions(res.data.questions);
      setAnswers(res.data.questions.map(() => ''));
      alert(JSON.stringify(res.data.questions));
    } catch (e) {
      alert('上传失败: ' + JSON.stringify(e));
      console.log('上传失败', e);
    }
  };

  const submitAnswers = async () => {
    let res = await axios.post('http://192.168.10.239:5000/correct', { username: 'test', answers });
    setResults(res.data.results);
  };

  const getWrongs = async () => {
    let res = await axios.get('http://192.168.10.239:5000/wrong_questions', { params: { username: 'test' } });
    setWrongs(res.data.wrongs);
  };

  const generateQ = async (kp: string) => {
    let res = await axios.post('http://192.168.10.239:5000/generate', { knowledge_point: kp });
    setGenQ(res.data.question);
  };

  return (
    <ScrollView style={{ marginTop: 40, padding: 10 }}>
      <Button title="选择试卷图片" onPress={pickImage} />
      {image && <Image source={{ uri: image }} style={{ width: 200, height: 200 }} />}
      <Button title="上传并识别" onPress={uploadImage} disabled={!image} />
      {questions.length > 0 && (
        <View>
          <Text>请填写你的答案：</Text>
          {questions.map((q, i) => (
            <View key={i}>
              <Text>{q.raw}</Text>
              {/* 如果是选择题，可以渲染选项 */}
              {q.type === '选择题' && q.options.map((opt: string, idx: number) => (
                <Text key={idx}>{opt}</Text>
              ))}
              <TextInput
                style={{ borderWidth: 1, marginBottom: 5 }}
                value={answers[i]}
                onChangeText={t => {
                  let a = [...answers];
                  a[i] = t;
                  setAnswers(a);
                }}
              />
            </View>
          ))}
          <Button title="提交批改" onPress={submitAnswers} />
        </View>
      )}
      {results.length > 0 && (
        <View>
          <Text>批改结果：</Text>
          {results.map((r, i) => (
            <Text key={i} style={{ color: r.is_right ? 'green' : 'red' }}>
              {r.question} 你的答案: {r.your_answer} 正确答案: {r.correct_answer} {r.is_right ? '✔' : '✘'}
            </Text>
          ))}
          <Button title="查看错题本" onPress={getWrongs} />
        </View>
      )}
      {wrongs.length > 0 && (
        <View>
          <Text>错题本：</Text>
          {wrongs.map((w, i) => (
            <Text key={i}>{w.question} 答案: {w.answer}</Text>
          ))}
          <Button title="为错题知识点生成新题" onPress={() => generateQ('分数加减法')} />
        </View>
      )}
      {genQ && <Text>AI生成新题：{genQ}</Text>}
    </ScrollView>
  );
}
