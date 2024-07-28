import React, { useState } from "react";
import styled from "styled-components";
import { TreeNode } from "../../api/types";

const TreeNodeContainer = styled.div<{ level: number }>`
  margin-left: ${(props) => props.level * 20}px;
  cursor: pointer;
  font-family: Arial, sans-serif;
  color: #333;
  font-size: 14px;
`;

interface TreeViewItemProps {
  node: TreeNode;
  level: number;
}

const TreeViewItem: React.FC<TreeViewItemProps> = ({ node, level }) => {
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
            <TreeViewItem key={child.id} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export default TreeViewItem;
