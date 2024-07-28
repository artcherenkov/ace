import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { setQuery } from "./searchSlice";

const SearchBar: React.FC = () => {
  const dispatch = useDispatch();
  const [query, setQueryState] = useState("");

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setQueryState(value);
    dispatch(setQuery(value));
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Search..."
        value={query}
        onChange={handleSearch}
        style={{
          padding: "8px",
          fontSize: "14px",
          border: "1px solid #ccc",
          borderRadius: "4px",
          width: "100%",
        }}
      />
    </div>
  );
};

export default SearchBar;
