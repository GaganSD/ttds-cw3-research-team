import './App.css';
import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import QEButton from './components/QueryExpansionButton';
import SearchField from './components/search';

//import { useParams } from 'react-router-dom'

import { useParams } from 'react-router-dom';
//>>>>>>> 8a10d7a19bd526b974cfed254b0322ec7bc41478

import Box from '@mui/material/Box';
import research_logo from './logos/researchlogomain.png';
import PageButton from './components/pagebutton';
import SwipeableTemporaryDrawer from './components/advancedOptions';
import PaperOrDS from './components/datasetorpaper';
import { useNavigate } from 'react-router-dom';

import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
// import { createTheme } from '@mui/material/styles';

function App() {

  const backend_server_ip = "http://34.145.46.81:5000/";

  let navigate = useNavigate();
  const routeChange = () => {
    if(search === ''|| !/^(?!\s+$).+/.test(search)){
    }
    else if (search.length > 27){
      setLongQuery(true);
    }
    else if( !/^[0-9a-zA-Z\s]*$/.test(search) ){
      setBadQuery(true);
 
    }
    else{
      let path = create_url(search, values.current);
      navigate(path);
    }
  }

  const [search, setSearch] = React.useState("");
  const showPageButton = React.useRef(false);
  const [pagenum, setPageNum] = React.useState(1);
  const [datasets, setDatasets] = React.useState(false);
  const [badquery, setBadQuery] = React.useState(false);
  const [longquery, setLongQuery] = React.useState(false);
  const [emptyresults, setEmptyResults] = React.useState(false);
  const [gobackbuttondisabled, setGoBackButtonDisabled] = React.useState(true);
  const [json_results, setJsonResults] = React.useState({"Results":[]});
  const [json_query_expansion, setJsonQE] = React.useState({QEResults:[]});
  const [json_spell_check, setJSONSC] = React.useState({ SCResults: [] });

  const values = React.useRef({
    algorithm: "FEATURED",
    searchtype: "DEFAULT",
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



  }

  const { query } = useParams();
  //const query_spaced = query.replaceAll('+', ' ');

  const getPoDS = (podval) => {
    if(podval === "Papers"){
      values.current.datasets = false;
      setDatasets(false);
    }
    else{

      values.current.datasets = true;
      setDatasets(true);
    }

  }

  const date_formatter = (date) =>{

    if (date === null){
      return "inf"
    }
    else{
      let day = date.getDate() + "";
      let month = (date.getMonth()+1) + "-";
      let year = date.getFullYear() + "-";

      return year+month+day;
    }

  }

  const create_url = (searchq, vals) =>{
    let url = "search/";
    url += SanitizeSearch(searchq).split(" ").join("+");
    url += "/";
    url += date_formatter(vals.range_from);
    url += "/";
    url += date_formatter(vals.range_to);
    url += "/";
    url += vals.algorithm.split(" ").join("_");
    url += "/";
    url += vals.searchtype.split(" ").join("_");
    url += "/";
    url += vals.datasets + "";
    url += "/";
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
      if (splitArr[arr_len - 2].length === 2 && splitArr[arr_len - 1].length === 2) {
        //this is using a ccTLD
        domain = splitArr[arr_len - 3] + '.' + domain;
      }
    }
    return domain;
  }


  function SearchFunc() {
    if(search === ""){
      // console.log("EMPTY SEARCH")

    }
    else if(search.length > 27){
      // console.log("Long query");
      setLongQuery(true);
    }
    else if( !/^[0-9a-zA-Z\s]*$/.test(search) || !/^(?!\s+$).+/.test(search)){
      setJsonResults({"Results": []})
      showPageButton.current = false;
      setBadQuery(true);

    }
    else{
      return fetch('http://34.145.46.81:5000/' + create_url(search, values.current)).then(response => response.json()).then(data => {
        if(data.Results.length === 0) {
            setEmptyResults(true);
        }
        else {
          setBadQuery(false);
          setEmptyResults(false);
          showPageButton.current = true;
          setJsonResults(data);
        }
      });
    }
  }

  function suggestions() {

    fetch(backend_server_ip + 'QE/' + search).then(response => response.json()).then(data => {
        setJsonQE(data);
    });
    fetch(backend_server_ip + 'SC/' + search).then(response => response.json()).then(data => {
        setJSONSC(data);
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
    var year;
    if (yr<100 && yr<=21){ //handling 2 digit years
        year="20"+yr;
    } else if (yr < 100) {
        year="19"+yr;
    } else {
      year = yr;
    }
    var d;
    if (isNaN(dateItems[monthIndex])){ //in case the month is written as a word
      d = new Date(string_date);
    } else {

      var month=parseInt(dateItems[monthIndex]);
      month-=1;

      d = new Date(year,month,dateItems[dayIndex]);
    }
    const monthNames = ["January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"];
    let formatted = monthNames[d.getMonth()] + ", " +  d.getFullYear();

    if (formatted === "undefined, NaN"){
      return "";
    }

    return formatted;
  }

  var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

  function abstractgenerator(text) {

    if (text!==""){
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
      return "-" + authors;
    } 
    else if (!(lower === "n/a" || lower === "na" || lower === "NA"
                 || lower === "n-a" || lower === "" || lower === " " || lower === "nan" || lower === "n.a.")){
      return "- " + authors;
    }
  }
  
  function TextEntered(searchval) {

    setSearch(searchval);
  }


  return (
    <div className="App" style={{
      marginLeft: '6em',
      marginRight: '6em'
    }}>


    <img src={research_logo} flex="1" height="350em" width="350em" resizeMode="contain" alt="Re-Search Brand Logo"/>

      <div className='Search' style={{
        width:'50%'
      }}>
        { badquery ? <SearchField
          style={{ maxWidth: '80%' }}
          parentCallback={TextEntered}
          error={true}
          text = {"Bad Query Was Received. We only allow english alphabets and whitespace!"}
        />
        : emptyresults ? <SearchField
          style = {{maxWidth:'80%'}}
          parentCallback={TextEntered}
          error={true}
          text = {"No matching records were found!"}
          />
          : longquery ? <SearchField
            initialvalue={query}
            style = {{maxWidth : '50%'}}
            parentCallback = {TextEntered}
            error={true}
            text={"Query too long, 27 characters or less please."}
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
      {/* <div>
        {json_query_expansion.QEResults.map(curr_elem => {
          return <Box>{curr_elem}</Box>;
        })}
      </div>
      <br/> */}

      <div style={{
        display: 'flex',
        justifyContent: 'center'
    }}>
        {json_query_expansion.QEResults.map((curr_qe, curr_key) => {
            return <Box key={curr_key}><font  color="#595F6A">{curr_qe}</font></Box>;
        })}
    </div>

    <div style={{
        display: 'flex',
        justifyContent: 'center'
    }}>
        {json_spell_check.SCResults.map((curr_qe, curr_key) => {
            return <Box key={curr_key}><font color="#595F6A">{curr_qe}</font></Box>;
        })}
    </div>


      <div className = 'Searchoptions' style={{
        display : "flex",
        flexDirection : "row"        
      }}>
        <ButtonGroup variant="contained" aria-label="outlined primary button group">
          <Button onClick={routeChange} variant="contained" style={{display: 'flex', justifyContent:'center'}}>
          Search
          </Button>
          <QEButton parentCallback={suggestions} />
        </ButtonGroup>

      </div>
      <br/>
      <PaperOrDS parentCallback={getPoDS}/>


    <div>

    {json_results.Results.map(curr_elem => {

      let std_date = standardize_dates(curr_elem.date);

      return <Box padding={0.2}>
        <p>
  
          <a href={curr_elem.url}> {curr_elem.title}</a><br/> 
          <font color="#595F6A" size="2">{fix_url(curr_elem.url)}  {std_date}  {authorlist(curr_elem.authors)}</font><br/> 
          <font color="#595F6A">{abstractgenerator(curr_elem.abstract)}</font><br/>
        </p></Box>;
    })}
    </div>
    <div style={{
      marginBottom: ".5em"
    }}> 
      <PageButton pagenum = {pagenum} disableback = {gobackbuttondisabled} show = {showPageButton.current} sexyProp={setPageNum} />
    </div>
    </div>
  )}

export default App;
