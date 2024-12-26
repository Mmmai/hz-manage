import smCrypto from "sm-crypto";


// AES加密函数
export function encrypt_sm4(key: string, mode: string, text: string): string {
  // 使用 CryptoJS 的 AES 方法加密文本
  // 加密
  // 获取后端的key
  // const key = "0123456789ABCDEF0123456789ABCDEF"
  // const mode = 'ecb'; // 设置SM4加解密模式（ecb、cbc、ctr等）
  const encoder = new TextEncoder();
  const bytes = encoder.encode(key);
  // const cipherText = smCrypto.sm4.encrypt(text, key, { mode });
  const cipherText = smCrypto.sm4.encrypt(text, bytes, { mode });
  return cipherText;
}
// AES解密函数
export function decrypt_sm4(key: string, mode: string, text: string): string {
  const encoder = new TextEncoder();
  const bytes = encoder.encode(key);
  const decryptedText = smCrypto.sm4.decrypt(text, bytes, { mode });
  return decryptedText
}
