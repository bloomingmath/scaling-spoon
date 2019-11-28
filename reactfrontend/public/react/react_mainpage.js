'use strict';

const e = React.createElement;

class SignupForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password1: '',
      password2: '',
    };

    this.handleUsernameChange = this.handleUsernameChange.bind(this);
    this.handleEmailChange = this.handleEmailChange.bind(this);
    this.handleFirstNameChange = this.handleFirstNameChange.bind(this);
    this.handleLastNameChange = this.handleLastNameChange.bind(this);
    this.handlePasswordOneChange = this.handlePasswordOneChange.bind(this);
    this.handlePasswordTwoChange = this.handlePasswordTwoChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleUsernameChange(event) {
    this.setState({username: event.target.value});
  }

  handleEmailChange(event) {
    this.setState({email: event.target.value});
  }

  handleFirstNameChange(event) {
    this.setState({first_name: event.target.value});
  }

  handleLastNameChange(event) {
    this.setState({last_name: event.target.value});
  }

  handlePasswordOneChange(event) {
    this.setState({password1: event.target.value});
  }

  handlePasswordTwoChange(event) {
    this.setState({password2: event.target.value});
  }

  handleSubmit(event) {
    const taxios = axios.create({
      baseURL: 'http://127.0.0.1:8000/',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'accept': 'application/json',
      }
    });
    event.preventDefault();
    // const qs = require('qs');
    axios.post('/register', Qs.stringify({
      username: this.state.username,
      email: this.state.email,
      first_name: this.state.first_name,
      last_name: this.state.last_name,
      password1: this.state.password1,
      password2: this.state.password2,
    }))
  .then(function (response) {
    console.log(response.data.access_token)
    if (response.data) {
      if (response.data.access_token) {
        Cookies.set('access_token', response.data.access_token, { expires: 1 })
      }
    }
    const resp = response;
    console.log(response);
  })
  .catch(function (error) {
    console.log(error);
  });
  }

  render() {
    return (
      <form method="post" onSubmit={this.handleSubmit}>
        <h2>Registrati</h2>
        <p className="hint-text">Completa i campi per la registrazione, oppure accedi al tuo profilo dalla barra di navigazione in alto.</p>
        <div className="form-group">
          <div className="row">
            <div className="col-xs-12 col-sm-6">
              <input type="text" className="form-control" name="first_name" placeholder="Nome" required={false}  value={this.state.first_name} onChange={this.handleFirstNameChange}  />
            </div>
            <div className="col-xs-12 col-sm-6">
              <input type="text" className="form-control" name="last_name" placeholder="Cognome" required={false}  value={this.state.last_name} onChange={this.handleLastNameChange} />
            </div>
          </div>
        </div>
        <div className="form-group">
           <input type="text" className="form-control" name="username" placeholder="Nome utente" required={false}  value={this.state.username} onChange={this.handleUsernameChange} />
        </div>
        <div className="form-group">
           <input type="email" className="form-control" name="email" placeholder="Email" required={false}  value={this.state.email} onChange={this.handleEmailChange} />
        </div>
        <div className="form-group">
          <input type="password" className="form-control" name="password1" placeholder="Password" required={false}  value={this.state.password1} onChange={this.handlePasswordOneChange} />
        </div>
        <div className="form-group">
          <input type="password" className="form-control" name="password2" placeholder="Conferma Password" required={false}  value={this.state.password2} onChange={this.handlePasswordTwoChange} />
        </div>
        <div className="form-group">
          <button type="submit" className="btn btn-success btn-lg btn-block">Crea profilo</button>
        </div>
      </form>
    );
  }
}


class ReactMainPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {access_token: Cookies.get('access_token')};
  }

  render() {
    if (this.state.access_token) {
      return (
        <div className="container">
          <div className="row">
            <div className="col-12">
                <h1>Benvenut@ Eternauta</h1>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="container">
        <div className="row">
          <div className="col-12">
            <div className="signup-form">
              <SignupForm />
            </div>
          </div>
        </div>
      </div>
    );
  }
}

const domContainer = document.querySelector('#react_mainpage_container');
ReactDOM.render(e(ReactMainPage), domContainer);



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





// <ul className="navbar-nav mr-auto">
// 				      <li className="nav-item active">
// 				        <a className="nav-link" href="#">Home <span className="sr-only">(current)</span></a>
// 				      </li>
// 				      <li className="nav-item">
// 				        <a className="nav-link" href="#">Gallery</a>
// 				      </li>
// 				      <li className="nav-item">
// 				        <a className="nav-link" href="#">Event</a>
// 				      </li>
// 				    </ul>
