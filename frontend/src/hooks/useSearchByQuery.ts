import { useQuery } from "@tanstack/react-query";
import { api } from "../api/api";
import { TreeNode } from "../api/types";
import { useEffect, useState } from "react";
import debounce from "lodash.debounce";

const searchSections = async (query: string): Promise<TreeNode[]> => {
  const { data } = await api.get<TreeNode[]>("/search", { params: { query } });
  return data;
};

export const useDebouncedSearchSections = (
  query: string,
  delay: number = 300,
) => {
  const [debouncedQuery, setDebouncedQuery] = useState(query);

  useEffect(() => {
    const handler = debounce((nextQuery: string) => {
      setDebouncedQuery(nextQuery);
    }, delay);

    handler(query);

    return () => {
      handler.cancel();
    };
  }, [query, delay]);

  return useQuery<TreeNode[], Error>({
    queryKey: ["search-sections", debouncedQuery],
    queryFn: () => searchSections(debouncedQuery),
    enabled: !!debouncedQuery,
  });
};
