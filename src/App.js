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
import Alert from '@mui/material/Alert';

import HelpButton from './components/HelpButton';
import Modal from '@mui/base/ModalUnstyled';

import Tab from '@mui/material/Tab';
import TabPanel from '@mui/lab/TabPanel';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import HelpDialog from "./components/helpdialog";

import { useEffect, useState } from "react";

import { ThemeProvider } from 'styled-components';
import { lightTheme, darkTheme } from './components/theme';
import { GlobalStyles } from './components/global';
//TODO: ADD Latex
function App() {
  const [theme, setTheme] = useState('light');
  const toggleTheme = () => {
    console.log("switch");
    if (theme === 'light') {
      setTheme('dark');
    } else {
      setTheme('light');
    }
  }

  const [search, setSearch] = React.useState('');
  const showPageButton = React.useRef(false);
  const [pagenum, setPageNum] = React.useState(1);
  const [datasets, setDatasets] = React.useState(false);
  const [badquery, setBadQuery] = React.useState(false);
  const [emptyresults, setEmptyResults] = React.useState(false);
  const [gobackbuttondisabled, setGoBackButtonDisabled] = React.useState(true);
  const [json_results, setJsonResults] = React.useState({"Results":[]});
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
  React.useEffect(() =>{
      if(pagenum === 1){
          setGoBackButtonDisabled(true);
      }
      else{
          setGoBackButtonDisabled(false);
      }
      console.log("CHANGINGGG");
      values.current.pagenum = pagenum;
      SearchFunc();

  },[pagenum]);
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
  const changePageNum = (val) => {
    setPageNum(pagenum + val);
  }

  const getPoDS = (podval) => {
    if(podval === "Papers"){
      values.current.datasets = false;
      setDatasets(false);
    }
    else{

      values.current.datasets = true;
      setDatasets(true);
    }

    // console.log(values.current.datasets);
  }

  const getPageNum = (pageNum) => {
    values.current.pagenum = pageNum;
    console.log(values.current.pagenum);
    SearchFunc();

  }

  const date_formatter = (date) =>{
    // console.log("HERE GOES THE DATE");
    console.log(date);
    if (date == null){
      return "inf"
    }
    else{
      let day = date.getDate() + "-";
      let month = (date.getMonth()+1) + "-";
      let year = date.getFullYear() + "";
      // console.log("HERE GOES THE DATE AGAINNNNNNN");
      console.log(day+month+year);
      // console.log("date over");
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

  function extractHostname(raw_url) {
    
    var hostname;  
    
    if (raw_url.indexOf("//") > -1) { // remove protocol
      hostname = raw_url.split('/')[2];
    } else {
      hostname = raw_url.split('/')[0];
    }
    hostname = hostname.split(':')[0]; // find & remove port number
    hostname = hostname.split('?')[0]; // find & remove "?"

    return hostname;
  }

  function fix_url(raw_url) {
    var domain = extractHostname(raw_url),
    splitArr = domain.split('.'),
    arr_len = splitArr.length;

    if (arr_len > 2) {
      domain = splitArr[arr_len - 2] + '.' + splitArr[arr_len - 1];
      //check to see if it's using a Country Code Top Level Domain (ccTLD) (i.e. ".me.uk")
      if (splitArr[arr_len - 2].length == 2 && splitArr[arr_len - 1].length == 2) {
        //this is using a ccTLD
        domain = splitArr[arr_len - 3] + '.' + domain;
      }
    }
    return domain;
  }

  function SearchFunc() {
    if(search === ""){
      console.log("EMPTY SEARCH")

    }
    else if( !/^[0-9a-zA-Z\s]*$/.test(search)){
      console.log("badquery");
      setJsonResults({"Results": []})
      showPageButton.current = false;
      setBadQuery(true);

    }
    else{
      return fetch('http://localhost:5000/' + create_url(search, values.current)).then(response => response.json()).then(data => {
        if(data.Results.length === 0){
            console.log("empty");
            setEmptyResults(true);
            console.log(emptyresults)
        }
        else{
          console.log("search complete");
          console.log(create_url(search, values.current));
          setBadQuery(false);
          setEmptyResults(false);
          showPageButton.current = true;
          setJsonResults(data);
        }
      });
    }
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
        if (text.length>100){
          return text.substring(0,100)+"...";
        }    
      } else {
        if (text.length>500){
        return text.substring(0,500) + "...";
        }
      }
    }
  }

  function authorlist(authors){
    var lower=authors.toLowerCase()
    if (authors.includes(",")){
      return "Authors: "+ authors;
    } else if (!(lower == "n/a" || lower == "na" || lower == "NA"
                 || lower == "n-a" || lower == "" || lower == " ")){
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


  return (
    <div className="App" style={{
      marginLeft: '6em',
      marginRight: '6em'
    }}>
    <ThemeProvider theme={theme === 'light' ? lightTheme : darkTheme}>
      <>
        <GlobalStyles />



    <img src={research_logo} width="300em" height="150em"/>
    <button onClick={toggleTheme}>Lights</button>

      <div className='Search' style={{
        width:'50%'
      }}>
        { badquery ? <SearchField
          style={{ maxWidth: '80%' }}
          parentCallback={TextEntered}
          error={true}
          text = {"Bad Query Was Received"}
        />
        : emptyresults ? <SearchField
            style = {{maxWidth:'80%'}}
            parentCallback={TextEntered}
            error={true}
            text = {"No Results were shown"}
            />
        : <SearchField
            style={{maxWidth : '80%'}}
            parentCallback={TextEntered}
            error={false}
            text = {"Query"}
          />
        }
      </div>
      <SwipeableTemporaryDrawer hysteresis="0.52" parentCallback={getOptions} datasets={datasets}/>
      <div>
        {json_query_expansion.QEResults.map(curr_elem => {
          return <Box>{curr_elem}</Box>;
        })}
      </div>
      <br/>


      <div className = 'Searchoptions' style={{
        display : "flex",
        flexDirection : "row"        
      }}>
        <ButtonGroup variant="contained" aria-label="outlined primary button group">
          <SearchButton parentCallback={() =>{
            console.log("yes");
            setPageNum(1);
            setGoBackButtonDisabled(true);
            console.log(pagenum);
            SearchFunc();
          }} />
          <QEButton parentCallback={QueryExpansion} />
        </ButtonGroup>

      </div>
      <br/>
      <PaperOrDS parentCallback={getPoDS}/>


    <div>

    {json_results.Results.map(curr_elem => {

      let std_date = standardize_dates(curr_elem.date);

      return <Box padding={0.2}>
        <p>
  
          {/* <Breadcrumbs color="grey" size="2" face="Tahoma" separator="›" href="/" aria-label="breadcrumb">
            {curr_elem.url}
          </Breadcrumbs> */}
          <a href={curr_elem.url}><font size="5">{curr_elem.title}</font></a><br/>
          <font color="#595F6A" size="2" face="Tahoma">{fix_url(curr_elem.url)} - {std_date}</font><br/>
          {/* <font color="#595F6A" face="Tahoma"></font><br/> */}
          <font color="#595F6A" face="Tahoma">{authorlist(curr_elem.authors)}</font>
          <font color="#595F6A">{abstractgenerator(curr_elem.abstract)}</font><br/>
        </p></Box>;
    })}
    </div>
    <div style={{
      marginBottom: ".5em"
    }}> 
      <PageButton pagenum = {pagenum} disableback = {gobackbuttondisabled} show = {showPageButton.current} sexyProp={setPageNum} />
    </div>
    {/* <div style={{
      position: 'fixed',
      bottom: 0,
    }}>
      { emptyresults ? <Alert severity="warning">No results were found</Alert> : null}
      {badquery ? <Alert severity="warning">Bad Search Query</Alert> : null}
    </div>
   */}
           </>
    </ThemeProvider>
    </div>
  )}

export default App;
