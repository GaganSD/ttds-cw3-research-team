import React, { Component } from 'react'
import ResultsData from './example.json'
class ResultList extends Component {
render(){
    return (
        <div>
        <h1>Test test</h1>
        {ResultsData.map((resultDetail, index)=>{
            return <h1>{resultDetail.title}</h1>})}
        </div>
    )
}

}
export default ResultList