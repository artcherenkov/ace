import { useQuery } from "@tanstack/react-query";
import { api } from "../api/api";
import { TreeNode } from "../api/types";

const fetchRootSections = async (): Promise<TreeNode[]> => {
  const { data } = await api.get<TreeNode[]>("/root-sections");
  return data;
};

export const useRootSections = () => {
  return useQuery<TreeNode[], Error>({
    queryKey: ["root-sections"],
    queryFn: fetchRootSections,
  });
};
