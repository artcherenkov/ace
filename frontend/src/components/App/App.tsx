import TreeView from "../TreeView/TreeView.tsx";
import mockData from "./mock.json";

const App = () => {
  return (
    <div>
      <TreeView data={mockData} />
    </div>
  );
};

export default App;
