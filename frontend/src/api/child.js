import { get, post, put, del } from './index.js';

export const getChildren = () => get('/api/children/');

export const getChild = (id) => get(`/api/children/${id}`);

export const createChild = (data) => post('/api/children/', data);

export const updateChild = (id, data) => put(`/api/children/${id}`, data);

export const deleteChild = (id) => del(`/api/children/${id}`);
