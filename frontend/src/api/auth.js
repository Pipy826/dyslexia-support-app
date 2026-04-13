import { post, get } from './index.js';
import { setToken, setUser } from '../utils/auth.js';

export const register = (data) => post('/api/auth/register', data);

export const login = (data) => post('/api/auth/login', data);

export const loginByCode = (phone, code) =>
  post(`/api/auth/login-by-code?phone=${encodeURIComponent(phone)}&code=${encodeURIComponent(code)}`);

export const getCurrentUser = () => get('/api/auth/me');

export const handleLoginSuccess = (res) => {
  setToken(res.access_token);
  setUser(res.user);
};

export const sendVerifyCode = (phone) => post('/api/auth/send-code', { phone });
