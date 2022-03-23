import * as React from 'react';
import { Box } from '@mui/system';
import { useParams } from 'react-router-dom'
import research_logo from '../logos/Re-Search-logos_transparent.png';
import SearchField from './search';
import SearchButton from './SearchButton';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import IconButton from '@mui/material/IconButton';
import { Button } from '@mui/material';
import SwipeableTemporaryDrawer from './advancedOptions';
import PaperOrDS from './datasetorpaper';
import ButtonGroup from '@mui/material/ButtonGroup';
import QEButton from './QueryExpansionButton';
import PageButton from './pagebutton';

export default function ResultsPage(props) {
    React.useEffect(() => {
        console.log("reeeeeee");
        let search_query = "search?" + (window.location.pathname).slice(8)
        console.log(search_query);
        return fetch('http://34.142.71.148:5000/' + search_query).then(response => response.json()).then(data => {
            console.log("search complete");
            console.log(create_url(search, values.current));
            setBadQuery(false);
            setEmptyResults(false);
            showPageButton.current = true;
            setJsonResults(data);
        });
    }, [])
    const { query, df, dt, alg, srchtyp, ds, pn } = useParams();
    console.log(query);
    console.log(df);
    console.log(df);
    const [search, setSearch] = React.useState('');
    const showPageButton = React.useRef(false);
    const [pagenum, setPageNum] = React.useState(1);
    const [datasets, setDatasets] = React.useState(false);
    const [badquery, setBadQuery] = React.useState(false);
    const [emptyresults, setEmptyResults] = React.useState(false);
    const [gobackbuttondisabled, setGoBackButtonDisabled] = React.useState(true);
    const [json_results, setJsonResults] = React.useState({ "Results": [] });
    const [json_query_expansion, setJsonQE] = React.useState({ QEResults: [] });
    const label = { inputProps: { 'aria-label': 'Switch demo' } };
    const values = React.useRef({
        algorithm: "Featured",
        searchtype: "Default",
        range_from: null,
        range_to: null,
        datasets: false,
        pagenum: 1
    });

    React.useEffect(() => {
        if (pagenum === 1) {
            setGoBackButtonDisabled(true);
        }
        else {
            setGoBackButtonDisabled(false);
        }
        console.log("CHANGINGGG");
        values.current.pagenum = pagenum;
        SearchFunc();

    }, [pagenum]);

    function standardize_dates(string_date) {

        string_date = string_date.replaceAll('-', '/');
        string_date = string_date.replace(/\s+/g, "");

        var _format = "d/m/y"
        var formatItems = _format.split('/');
        var dateItems = string_date.split('/');
        var dayIndex = formatItems.indexOf("d");
        var monthIndex = formatItems.indexOf("m");
        var yearIndex = formatItems.indexOf("y");

        var yr = parseInt(dateItems[yearIndex]);
        if (yr < 100 && yr <= 21) { //handling 2 digit years
            var year = "20" + yr;
        } else if (yr < 100) {
            var year = "19" + yr;
        } else {
            var year = yr;
        }

        if (isNaN(dateItems[monthIndex])) { //in case the month is written as a word
            var d = new Date(string_date);
        } else {

            var month = parseInt(dateItems[monthIndex]);
            month -= 1;

            var d = new Date(year, month, dateItems[dayIndex]);
        }
        const monthNames = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"];
        let formatted = monthNames[d.getMonth()] + ", " + d.getFullYear();

        return formatted;
    }

    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    function abstractgenerator(text) {

        if (text != "") {
            if (isMobile) {
                if (text.length > 100) {
                    return text.substring(0, 100) + "...";
                }
            } else {
                if (text.length > 500) {
                    return text.substring(0, 500) + "...";
                }
            }
        }
    }

    function authorlist(authors) {
        var lower = authors.toLowerCase()
        if (authors.includes(",")) {
            return authors;
        } else if (!(lower == "n/a" || lower == "na" || lower == "NA"
            || lower == "n-a" || lower == "" || lower == " ")) {
            return authors;
        }
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

    function SearchFunc() {
        if (search === "") {
            console.log("EMPTY SEARCH")

        }
        else if (!/^[0-9a-zA-Z\s]*$/.test(search)) {
            console.log("badquery");
            setJsonResults({ "Results": [] })
            showPageButton.current = false;
            setBadQuery(true);

        }
        else {
            return fetch('http://34.142.71.148:5000/' + create_url(search, values.current)).then(response => response.json()).then(data => {
                console.log(create_url(search, values.current));
                if (data.Results.length === 0) {
                    console.log("empty");
                    setEmptyResults(true);
                    console.log(emptyresults)
                }
                else {
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



    const getPoDS = (podval) => {
        if (podval === "Papers") {
            values.current.datasets = false;
            setDatasets(false);
        }
        else {

            values.current.datasets = true;
            setDatasets(true);
        }
    }

    const date_formatter = (date) => {
        // console.log("HERE GOES THE DATE");
        console.log(date);
        if (date == null) {
            return "inf"
        }
        else {
            let day = date.getDate() + "-";
            let month = (date.getMonth() + 1) + "-";
            let year = date.getFullYear() + "";
            // console.log("HERE GOES THE DATE AGAINNNNNNN");
            console.log(day + month + year);
            // console.log("date over");
            return day + month + year;
        }

    }

    function SanitizeSearch(searchval) {
        searchval.replaceAll("/", " ");
        return searchval;
    }


    const create_url = (searchq, vals) => {
        let url = "search?q=";
        url += SanitizeSearch(searchq).split(" ").join("+");
        url += "/df=";
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
    function TextEntered(searchval) {

        setSearch(searchval);
    }

    function getOptions(type, optval) {
        if (type === "algorithms") {
            values.current.algorithm = optval;
        }
        else if (type === "searchtype") {
            values.current.searchtype = optval;
        }
        else if (type === "author") {
            values.current.author_text = optval;
        }
        else if (type === "date_from") {
            values.current.range_from = optval;
        }
        else if (type === "date_to") {
            values.current.range_to = optval;
        }

        console.log(values);
        console.log(date_formatter(values.current.range_from));
    }



    return (
        <div className='ResultsPage'>
            <div className='searchBar'>
                <Box
                    sx={{
                        width: '100%',
                        height: "5em",
                        backgroundColor: '#f5f5f5'
                    }}>
                    <div style={{
                        display: 'flex',
                        flexDirection: 'row',
                        justifyContent: 'center'
                    }}>
                        <div className='Options' style={{
                            marginRight: '10em',
                            marginTop: '1.5em'
                        }}>
                            <SwipeableTemporaryDrawer hysteresis="0.52" parentCallback={getOptions} datasets={datasets} />
                        </div>
                        <h1>Re-Search</h1>
                        <div className='SearchField' style={{
                            width: '30%',
                            marginTop: '1.5em',
                            marginLeft: '1em'
                        }}>
                            {badquery ? <SearchField
                                style={{ maxWidth: '80%' }}
                                parentCallback={TextEntered}
                                error={true}
                                text={"Bad Query Was Received"}
                            />
                                : emptyresults ? <SearchField
                                    style={{ maxWidth: '80%' }}
                                    parentCallback={TextEntered}
                                    error={true}
                                    text={"No Results were shown"}
                                />
                                    : <SearchField
                                        style={{ maxWidth: '80%' }}
                                        parentCallback={TextEntered}
                                        error={false}
                                        text={"Query"}
                                    />
                            }
                        </div>
                        <div className='SearchButton' style={{
                            marginTop: '1.5em',
                            marginLeft: '1em'
                        }}>
                            <ButtonGroup variant="contained" aria-label="outlined primary button group">
                                <SearchButton parentCallback={() => {
                                    console.log("yes");
                                    setPageNum(1);
                                    setGoBackButtonDisabled(true);
                                    console.log(pagenum);
                                    SearchFunc();
                                }} />
                                <QEButton parentCallback={QueryExpansion} />
                            </ButtonGroup>
                        </div>
                        <div style={{
                            marginTop: "1em",
                            marginLeft: "1em"
                        }}>
                            <PaperOrDS parentCallback={getPoDS} />
                        </div>
                    </div>
                </Box>
                {/* <p>moneybag yo</p> */}
                <div className='results' style={{
                    marginLeft: '20em',
                    marginRight: '20em'
                }}>

                    {json_results.Results.map(curr_elem => {

                        let std_date = standardize_dates(curr_elem.date);

                        return <Box padding={0.2}>
                            <p>

                                {/* <Breadcrumbs color="grey" size="2" face="Tahoma" separator="›" href="/" aria-label="breadcrumb">
                        {curr_elem.url}
                    </Breadcrumbs> */}
                                {/* TODO: Enable latex formatting in author title
                    TODO: Remove latex & markdown formatting in description */}
                                <a href={curr_elem.url}><font size="5">{curr_elem.title}</font></a><br />
                                <font color="#595F6A" size="2" face="Tahoma">{fix_url(curr_elem.url)} - {std_date} - {authorlist(curr_elem.authors)}</font><br />
                                {/* <font color="#595F6A" face="Tahoma"></font><br/> */}
                                <font color="#595F6A">ㅤ{abstractgenerator(curr_elem.abstract)}</font><br />
                            </p></Box>;
                    })}
                </div>
                <div style={{
                    marginBottom: ".5em"
                }}>
                    <PageButton pagenum={pagenum} disableback={gobackbuttondisabled} show={showPageButton.current} sexyProp={setPageNum} />
                </div>
            </div>
        </div>
    )
}