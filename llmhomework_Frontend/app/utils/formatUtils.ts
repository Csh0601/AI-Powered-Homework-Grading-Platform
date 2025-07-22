// 格式化日期为 yyyy-MM-dd HH:mm:ss
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

// 截取字符串，超出部分加省略号
export function truncate(str: string, maxLength: number): string {
  if (!str) return '';
  return str.length > maxLength ? str.slice(0, maxLength) + '...' : str;
}

// 标记是否正确，返回 ✔/✘
export function markCorrect(isCorrect: boolean): string {
  return isCorrect ? '✔' : '✘';
}
