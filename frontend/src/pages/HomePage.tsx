import React from "react";
import { useSelector } from "react-redux";
import { RootState } from "../store/store";
import TreeView from "../components/TreeView/TreeView";
import SearchBar from "../features/search/SearchBar";
import styled from "styled-components";

const Column = styled.section`
  width: 50%;
`;

const HomePage: React.FC = () => {
  const query = useSelector((state: RootState) => state.search.query);

  return (
    <Column>
      <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
        <h1 style={{ color: "#2c3e50" }}>Search and Browse</h1>
        <SearchBar />
        <TreeView query={query} />
      </div>
    </Column>
  );
};

export default HomePage;
