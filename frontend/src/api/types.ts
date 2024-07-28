export interface TreeNode {
  id: number;
  name: string;
  type: string;
  code: string;
  parent_section_id: number | null;
  children: TreeNode[];
}
