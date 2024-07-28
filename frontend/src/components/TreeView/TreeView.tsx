import { FC, useState } from "react";
import styled from "styled-components";

interface TreeNode {
  id: number;
  name: string;
  type: string;
  code: string;
  parent_section_id: number | null;
  children: TreeNode[];
}

interface TreeItemProps {
  node: TreeNode;
  level: number;
}

const TreeNodeContainer = styled.div<{ level: number }>`
  margin-left: ${(props) => props.level * 20}px;
  cursor: pointer;
  font-family: "Arial, sans-serif", sans-serif;
  color: #333;
  font-size: 14px;
`;

const TreeItem: FC<TreeItemProps> = ({ node, level }) => {
  const [isOpen, setIsOpen] = useState(false);
  const hasChildren = node.children && node.children.length > 0;

  const toggleOpen = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div>
      <TreeNodeContainer level={level} onClick={toggleOpen}>
        {hasChildren && <span>{isOpen ? "−" : "+"}</span>}
        <span>
          {" "}
          {node.name} ({node.code})
        </span>
      </TreeNodeContainer>
      {isOpen && hasChildren && (
        <div>
          {node.children.map((child) => (
            <TreeItem key={child.id} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

interface TreeViewProps {
  data: TreeNode[];
}

const TreeView: FC<TreeViewProps> = ({ data }) => {
  return (
    <div>
      {data.map((node) => (
        <TreeItem key={node.id} node={node} level={0} />
      ))}
    </div>
  );
};

export default TreeView;
