import React from "react";
import TreeViewItem from "./TreeViewItem";
import { useRootSections } from "../../hooks/useRootSections";
import { TreeNode } from "../../api/types";
import { useDebouncedSearchSections } from "../../hooks/useSearchByQuery.ts";

interface TreeViewProps {
  query: string;
}

const TreeView: React.FC<TreeViewProps> = ({ query }) => {
  const {
    data: rootData,
    isLoading: isRootLoading,
    isError: isRootError,
  } = useRootSections();

  const {
    data: searchData,
    isLoading: isSearchLoading,
    isError: isSearchError,
  } = useDebouncedSearchSections(query);

  const data = query ? searchData : rootData;
  const isLoading = query ? isSearchLoading : isRootLoading;
  const isError = query ? isSearchError : isRootError;

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error loading data</div>;

  return (
    <div>
      {data?.map((node: TreeNode) => (
        <TreeViewItem key={node.id} node={node} level={0} />
      ))}
    </div>
  );
};

export default TreeView;
