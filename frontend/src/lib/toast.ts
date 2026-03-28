import { toast as sonnerToast } from "sonner";

export { sonnerToast as toast };

export const toastSuccess = (message: string): void => {
  sonnerToast.success(message);
};

export const toastError = (message: string): void => {
  sonnerToast.error(message);
};

export const toastInfo = (message: string): void => {
  sonnerToast.info(message);
};

export const toastLoading = (message: string): void => {
  sonnerToast.loading(message);
};
