import axios from "axios";

const http = axios.create({ baseURL: "/", timeout: 15000 });

export interface Item { value: string; label: string }
export interface InitResp { errorCode: string; pageList?: Item[]; kbnList?: Item[] }
export interface UrlResp { errorCode: string; url?: string }

export const fetchInit = async (): Promise<InitResp> =>
  (await http.post("/R60Login/init", { params: {} })).data;

export const postLogin = async (params: Record<string, string>) =>
  (await http.post("/R60Login/login", { params })).data;

export const postGenerateUrl = async (params: Record<string, string>): Promise<UrlResp> =>
  (await http.post("/R60Login/generateUrl", { params })).data;
