const Welcome = (info) => {
    return <h1>Hi {info.name}</h1>;
}

const rootElement = document.getElementById("root");(rootElement)
ReactDOM.render(<Welcome name="Sidney" />, rootElement);