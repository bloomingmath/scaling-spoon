'use strict';

const e = React.createElement;

class ReactNavbar extends React.Component {
  constructor(props) {
    super(props);
    this.state = { show_form: false };
  }

  render() {
    if (this.state.logged) {
      return 'You are logged';
    }

    return (
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark fixed-top rounded">
			  <a className="navbar-brand" href="#">Bloomingmath</a>
			  <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
			    <i className="fa fa-sign-in"></i>
			  </button>
			  <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav mr-auto">
			      {/*
              <li class="nav-item active">
              <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>
              </li>
              <li class="nav-item">
              <a class="nav-link" href="#">Gallery</a>
              </li>
              <li class="nav-item">
              <a class="nav-link" href="#">Event</a>
              </li>
            */}
			    </ul>
			    <form className="form-inline my-2 my-lg-0">
			    	<div className="col-xs-12 col-sm-5 col-md-auto px-0 pr-sm-1">
				      <div className="input-group">
				        <div className="input-group-prepend">
				          <div className="input-group-text"><i className="fa fa-user"></i></div>
				        </div>
				        <input type="text" className="form-control" id="exampleInputEmail1" aria-describedby="emailHelp" placeholder="Nome utente" />
				      </div>
				    </div>
				    <div className="col-xs-12 col-sm-5 col-md-auto px-0 pr-sm-1">
				      <div className="input-group">
				        <div className="input-group-prepend">
				          <div className="input-group-text"><i className="fa fa-lock"></i></div>
				        </div>
				        <input type="password" className="form-control" id="inlineFormInputGroup" placeholder="Password" />
				      </div>
				    </div>
				    <div className="col-xs-12 col-sm-2 col-md-auto px-0">
		      		<button className="btn btn-primary my-2 my-sm-0 w-100" type="submit">Login</button>
		      	</div>
			    </form>
			  </div>
			</nav>
    );
  }
}

const domContainer = document.querySelector('#react_navbar_container');
ReactDOM.render(e(ReactNavbar), domContainer);



// <form className="form-inline">
//   <div className="clearfix">
//     <input className="form-control mr-sm-2" type="text" placeholder="username" aria-label="username" id="username"/>
//     <input className="form-control mr-sm-2" type="password" placeholder="password" aria-label="password" id="password"/>
//     <button type="button" className="btn btn-secondary float-right" onClick={() => this.setState({ show_form: true })}>
//       Login
//     </button>
//   </div>
// </form>

// <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
//   <span className="sr-only">Toggle navigation</span>
//   <span className="icon-bar"></span>
//   <span className="icon-bar"></span>
//   <span className="icon-bar"></span>
// </button>





// <ul class="navbar-nav mr-auto">
// 				      <li class="nav-item active">
// 				        <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>
// 				      </li>
// 				      <li class="nav-item">
// 				        <a class="nav-link" href="#">Gallery</a>
// 				      </li>
// 				      <li class="nav-item">
// 				        <a class="nav-link" href="#">Event</a>
// 				      </li>
// 				    </ul>
