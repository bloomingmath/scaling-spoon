'use strict';

const e = React.createElement;

class OrderingBadges extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      text_intro: text_intro,
      content: content,
      ordered_list: content['ordered_list'],
    };
  }

  render() {
    return (
      <div class="container">
        <p>{ this.state.text_intro }</p>
        <li></li>
      </div>
    );
  }
}
//
// function OrderingBadges(props) {
//   return (
//     <div className="container">
//       <p>{ text_intro }</p>
//     </div>
//   )
// }


const domContainer = document.querySelector('#react_question_container');
ReactDOM.render(e(OrderingBadges), domContainer);
