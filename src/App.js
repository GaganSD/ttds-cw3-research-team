import './App.css';
import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import SearchButton from './components/SearchButton';
import QEButton from './components/QueryExpansionButton';
import SearchField from './components/search';
import UseSwitchesCustom from './components/toggle';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Options from './components/options'
import Box from '@mui/material/Box';
import research_logo from './logos/Re-Search-logos_transparent.png';

import Switch from '@mui/material/Switch';
import SwipeableTemporaryDrawer from './components/advancedOptions';

function App() {

  const [search, setSearch] = React.useState('');
  const [json_results, setJsonResults] = React.useState({Results:[]});
  const [json_query_expansion, setJsonQE] = React.useState({QEResults:[]});
  const label = { inputProps: { 'aria-label': 'Switch demo' } };
  const [values,setValues] = React.useState({
    oldest: false,
    latest: false,
    featured: true,
    authors: true,
    author_text:'',
    range_from:null,
    range_to: null
  })

  function getOptions(optval){
    setValues(optval);
    // console.log(values);

  }

  function SearchFunc() {

    return fetch('http://127.0.0.1:5000/' + search).then(response => response.json()).then(data => {
      setJsonResults(data);
    });
  }

  function QueryExpansion() {
    
    return fetch('http://127.0.0.1:5000/QE/' + search).then(response => response.json()).then(data => {
      setJsonQE(data);
    });
  }

  function standardize_dates(string_date) {

    string_date=string_date.replaceAll('-','/');
    string_date = string_date.replace(/\s+/g,"");

    var _format="d/m/y"
    var formatItems=_format.split('/');
    var dateItems=string_date.split('/');
    var dayIndex=formatItems.indexOf("d");
    var monthIndex=formatItems.indexOf("m");
    var yearIndex=formatItems.indexOf("y");

    var yr = parseInt(dateItems[yearIndex]);
    if (yr<100 && yr<=21){ //handling 2 digit years
        var year="20"+yr;
    } else if (yr < 100) {
        var year="19"+yr;
    } else {
      var year = yr;
    }

    if (isNaN(dateItems[monthIndex])){ //in case the month is written as a word
      var d = new Date(string_date);
    } else {
      
      var month=parseInt(dateItems[monthIndex]);
      month-=1;

      var d = new Date(year,month,dateItems[dayIndex]);
    }

    let formatted = [String ("0" + d.getDate()).slice(-2), String ("0" + (d.getMonth() +1)).slice(-2), d.getFullYear()].join('/');

    return formatted;
  }

  var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

  function abstractgenerator(text) {

    if (text!=""){
      if (isMobile){
        return text.substring(0,100)+"...";
      } else {
        return text.substring(0,500)+"...";
      }
    }
  }

  function authorlist(authors){
    var lower=authors.toLowerCase()
    if (authors.includes(",")){
      return "Authors: "+ authors;
    } else if (!(lower == "n/a" || lower == "na"
                 || lower == "n-a" || lower == "")){
      return "Author: "+ authors;
    }
  }


  function BasicSwitches() {
    return (
      <div>
        <Switch {...label} defaultChecked />
        <Switch {...label} />
        <Switch {...label} disabled defaultChecked />
        <Switch {...label} disabled />
      </div>
    );
  }
  
  function TextEntered(searchval) {

    setSearch(searchval);
  }

  return (
    <div className="App" style={{

      marginLeft: '5em',
      marginRight: '5em'
    }}>
    <div className="toggle_switch" float="center" id="toggle_switch"></div>

    <img src={research_logo} width="300em" height="150em"/>

    <UseSwitchesCustom  float="right" parentCallback={BasicSwitches} />
      <div className='SearchOptions' style={{
        width:'50%'
      }}>
        <SearchField
          style={{ maxWidth: '80%' }}
          parentCallback={TextEntered}
        />
      </div>
      <SwipeableTemporaryDrawer parentCallback={getOptions}/>
      <div>
        {json_query_expansion.QEResults.map(curr_elem => {
          return <Box>
            {/* TODO: make this display pretty */}
            {curr_elem}
          </Box>;
        })}
      </div>

      <ButtonGroup variant="contained" aria-label="outlined primary button group">

        <SearchButton parentCallback={SearchFunc} />
        <QEButton parentCallback={QueryExpansion} />

      </ButtonGroup>
    <div>

    {json_results.Results.map(curr_elem => {

      let std_date = standardize_dates(curr_elem.date);

      return <Box
      padding={1}
      // if statements: one for modile devices, one for all desktops. 
      >
        <p>
          <p><font COLOR="grey" SIZE="2" face="Arial">{curr_elem.url}</font></p>
          <a href={curr_elem.url}><font COLOR="green" SIZE="5" face="Arial">{curr_elem.title}</font></a>
          <p><font COLOR="grey" face="Arial">{std_date}</font></p>
          <p><font face="Arial">{abstractgenerator(curr_elem.abstract)}</font></p>
          <p><font face="Arial">{authorlist(curr_elem.authors)}</font></p>
        </p></Box>;
    })}
    </div>
    </div>
  )}

export default App;