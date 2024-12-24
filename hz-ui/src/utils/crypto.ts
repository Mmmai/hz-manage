import CryptoJS from "crypto-js";


// AES加密函数
export function encrypt(text: string, key: string): string {
  // 使用 CryptoJS 的 AES 方法加密文本
  // 加密
  const keyF = CryptoJS.enc.Utf8.parse(btoa(key.substring(0, 32).padEnd(32, "\0")));
  const encrypted = CryptoJS.AES.encrypt(plainText, keyF, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7,
  });

  return encrypted.toString();
}
// AES解密函数
export function decrypt(encryptData: string, key: string): string {
  try {
    // 解密
    const bytes = CryptoJS.AES.decrypt(encryptData, key, {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7,
    });
    return bytes.toString(CryptoJS.enc.Utf8);
  } catch (error) {
    console.log(error)
    // 如果解密失败，返回空字符串
    return "";
  }
}
