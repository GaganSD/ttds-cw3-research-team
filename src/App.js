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
import PageButton from './components/pagebutton';
import Switch from '@mui/material/Switch';
import Link from '@mui/material/Link';
import SwipeableTemporaryDrawer from './components/advancedOptions';
import PaperOrDS from './components/datasetorpaper';

import HelpButton from './components/HelpButton';
import Modal from '@mui/base/ModalUnstyled';

import Tab from '@mui/material/Tab';
import TabPanel from '@mui/lab/TabPanel';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import HelpDialog from "./components/helpdialog"

function App() {

  const [search, setSearch] = React.useState('');
  const showPageButton = React.useRef(false);
  const pageNum = React.useRef(1);
  const resetPageButton = React.useRef(false);
  const [json_results, setJsonResults] = React.useState({Results:[]});
  const [json_query_expansion, setJsonQE] = React.useState({QEResults:[]});
  const label = { inputProps: { 'aria-label': 'Switch demo' } };
  const values = React.useRef({
    algorithm: "Featured",
    searchtype: "Default",
    range_from:null,
    range_to: null,
    datasets: false,
    pagenum: 1
  });

  function getOptions(type,optval){
    if (type === "algorithms"){
      values.current.algorithm = optval;
    }
    else if (type === "searchtype"){
      values.current.searchtype = optval;
    }
    else if (type === "author"){
      values.current.author_text = optval;
    }
    else if (type === "date_from"){
      values.current.range_from = optval;
    }
    else if (type === "date_to"){
      values.current.range_to = optval;
    }

    console.log(values);
    console.log(date_formatter(values.current.range_from));


  }

  const getPoDS = (podval) => {
    if(podval === "Papers"){
      values.current.datasets = false;
    }
    else{

      values.current.datasets = true;
    }

    console.log(values.current.datasets);
  }

  const getPageNum = (pageNum) => {
    values.current.pagenum = pageNum;
    console.log(values.current.pagenum);
    SearchFunc();

  }

  const date_formatter = (date) =>{
    console.log("HERE GOES THE DATE");
    console.log(date);
    if (date == null){
      return "inf"
    }
    else{
      let day = date.getDate() + "-";
      let month = (date.getMonth()+1) + "-";
      let year = date.getFullYear() + "";
      console.log("HERE GOES THE DATE AGAINNNNNNN");
      console.log(day+month+year);
      console.log("date over");
      return day+month+year;
    }

  }

  const create_url = (searchq, vals) =>{
    let url = "search?q=";
    url += SanitizeSearch(searchq).split(" ").join("+");
    url += "/df=";
    // console.log(date_formatter(vals.range_from));
    url += date_formatter(vals.range_from);
    url += "/dt=";
    url += date_formatter(vals.range_to);
    url += "/alg=";
    url += vals.algorithm.split(" ").join("_");
    url += "/srchtyp=";
    url += vals.searchtype.split(" ").join("_");
    url += "/ds=";
    url += vals.datasets + "";
    url += "/pn=";
    url += vals.pagenum + "";
    url += "/";

    return url

  }

  function SanitizeSearch(searchval) {
    searchval.replaceAll("/", " ");
    return searchval;
  }

  function SearchFunc() {
    showPageButton.current = true;
    return fetch('http://34.142.71.148:5000/' + create_url(search, values.current)).then(response => response.json()).then(data => {
      setJsonResults(data);
    });
  }

  function QueryExpansion() {
    
    console.log(create_url(search, values.current));
    return fetch('http://34.142.71.148:5000/QE/' + search).then(response => response.json()).then(data => {
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

  const [open, setOpen] = React.useState(false);

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const [value2, setValue2] = React.useState('1');

  const handleTabChange = (event, newValue) => {
    setValue2(newValue);
  };

  const resetPageButtonFunc = () => {
    resetPageButton.current = true;
    resetPageButton.current = false;

  }

  return (
    <div className="App" style={{
      marginLeft: '6em',
      marginRight: '6em'
    }}>
    <div className="toggle_switch" float="center" id="toggle_switch"></div>

    <img src={research_logo} width="300em" height="150em"/>

    <UseSwitchesCustom  float="right" parentCallback={BasicSwitches} />
      <div className='Search' style={{
        width:'50%'
      }}>
        <SearchField
          style={{ maxWidth: '80%' }}
          parentCallback={TextEntered}
        />
      </div>
      <SwipeableTemporaryDrawer hysteresis="0.52" parentCallback={getOptions}/>
      <div>
        {json_query_expansion.QEResults.map(curr_elem => {
          return <Box>{curr_elem}</Box>;
        })}
      </div>



      <div className = 'Searchoptions' style={{
        display : "flex",
        flexDirection : "row"        
      }}>
        <ButtonGroup variant="contained" aria-label="outlined primary button group">
          <SearchButton parentCallback={() =>{
            // resetPageButtonFunc();
            SearchFunc();
          }} />
          <QEButton parentCallback={QueryExpansion} />
        </ButtonGroup>
        <div style = {{
          paddingLeft : "5em"
        }}>
          <PaperOrDS parentCallback={getPoDS}/>
        </div>
      </div>
      


    <div>

    {json_results.Results.map(curr_elem => {

      let std_date = standardize_dates(curr_elem.date);

      return <Box padding={0.2}>
        <p>
  
          {/* <Breadcrumbs color="grey" size="2" face="Tahoma" separator="›" href="/" aria-label="breadcrumb">
            {curr_elem.url}
          </Breadcrumbs> */}
          <font color="grey" size="2" face="Tahoma">{curr_elem.url}</font><br/><br/>
          <a href={curr_elem.url}><font color="blue" size="5" face="Tahoma">{curr_elem.title}</font></a>
          <p><font color="grey" face="Tahoma">{std_date}</font></p>
          <p><font face="Tahoma">{abstractgenerator(curr_elem.abstract)}</font></p>
          <p><font face="Tahoma">{authorlist(curr_elem.authors)}</font></p>
        </p></Box>;
    })}
    </div>
    <div style={{
      marginBottom : "2 em"
    }}> 
      <PageButton show = {showPageButton.current} parentCallback={getPageNum} reRender = {resetPageButton.current}/>
    </div>

    </div>
  )}

export default App;
