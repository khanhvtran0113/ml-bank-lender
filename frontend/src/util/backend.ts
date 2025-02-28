import axios from "axios";

const BACKEND_URL = "http://127.0.0.1:5000";

export async function clearMessages(lendeeName: string) {
  return post("/clear_thread", { lendee_name: lendeeName });
}

export async function sendMessage(lendeeName: string, message: string) {
  return post("/ask_question", { lendee_name: lendeeName, question: message });
}

export async function getLendees() {
  return get("/api/lendees", {});
}

export async function getLendeeInfo(lendeeName: string) {
  return get(`/lendees/${lendeeName}`, {});
}

export async function upload(formData: FormData) {
  return post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}

export async function createLendee(lendeeName: string) {
  return post("/api/lendees", { name: lendeeName });
}

async function get<T>(relativeUrl: string, payload: any): Promise<T> {
  return (await axios.get<T>(BACKEND_URL + relativeUrl, payload)).data;
}

async function post<T>(
  relativeUrl: string,
  payload: any,
  headers?: any
): Promise<T> {
  return (await axios.post<T>(BACKEND_URL + relativeUrl, payload, headers))
    .data;
}
