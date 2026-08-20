export const api = {
  get: async (path: string) => {
    return fetch(path).then((res) => res.json());
  },
};
