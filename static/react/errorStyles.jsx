const App = () => {


    const css = `
    #root {
        height: 200px;
        background: red;
    }`

	return (
		<div>
			<style>
                {css}
            </style>
            <p>Hi</p>
		</div>
	)
};




const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);
