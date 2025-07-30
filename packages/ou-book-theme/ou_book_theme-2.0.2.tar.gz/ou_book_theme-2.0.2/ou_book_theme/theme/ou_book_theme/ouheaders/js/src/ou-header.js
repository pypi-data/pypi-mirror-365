
// Digital Analytix (Comscore) tracking code
// May 2011 - Steve Bannister (c) Open University
// Last amended 28 October 2011 (SB)
//
// LIVE IMPLEMENTATION MUST BE MINIFIED


var ou_ca_pub = ["www", "www3", "www2", "www8", "css2", "css3", "msds", "search", "students", "stem", "fass", "wels", "business-school", "law-school", "help"];
var ou_ca_med = ["openlearn", "labspace", "podcast"];
var ou_ca_vle = ["learn", "learn0", "learn1", "learn2", "learn3", "learn4"];
var ou_ca_int = ["intranet", "intranet6", "intranet-gw", "share", "intranet7", "intranet8"];
// ACCT tracking
var ou_ca_test = ["msds-acct", "www3-acct", "css2-acct", "csintra1", "learnacct", "learn2acct", "learn3acct", "learn4acct", "www-acct", "www8-acct", "www2-acct", "exa-acct", "www-pf-acct"];
ou_ca_test = ou_ca_test.concat(["stem-acct", "fass-acct", "wels-acct", "business-school-acct", "law-school-acct", "help-acct"]);
// TEST tracking
ou_ca_test = ou_ca_test.concat(["gaffer", "cms-test", "cms-app-test", "cms-app-trng", "exa-test", "search-test", "csr-pizza14-tst", "help-test"]);
// DEV tracking
ou_ca_test = ou_ca_test.concat(["stem-dev", "fass-dev", "wels-dev", "business-school-dev", "law-school-dev", "localhost-dev", "help-dev"]);

var ou_tracked_domains = ["//openlearn", "//labspace", "//search", "//fass", "//wels", "//stem", "//business-school", "//law-school", "//localhost-dev"];

var ou_pm_page = ["1a/o1aprospchoice.asp"];
var ou_pm_var = ["catcode"];
var ou_tracked = 0;
var ou_sitename, ou_pagename = "", ou_nsbaseurl = "";
var ou_firsttime_only = 0;		// Temp, to stop event tracking from using new-world tracking

/**
 *  @deprecated since v1.0.1.38
 */
function ou_sitestat() {
    console.warn("Calling deprecated function - ou_sitestat. Please delete all calls to this");
}

/**
 *  @deprecated since v1.0.1.38
 */
function ou_sitestat_manual(pg) {
    console.warn("Calling deprecated function - ou_sitestat_manual. Please delete all calls to this");
}

/**
 *  @deprecated since v1.0.1.38
 */
function ou_sitestat_retrieve_experiments(pg) {
    console.warn("Calling deprecated function - ou_sitestat_manual. Please delete all calls to this");
}

function ou_usertype(pg) {
    // Get value of SAMS2session cookie
    var ck2 = document.cookie + ";";
    var i = ck2.indexOf("SAMS2session=");
    if (i < 0) return pg;
    i += 13;
    var ck = ck2.substr(i, ck2.indexOf(";", i) - i) + "&";

    // Find user values...
    var types = "";

    var x = ou_getusertype(ck, "samsStudentPI=");
    if (x != null) {
        var prospect = 0;
        // We need to further check if the user is a prospect by checking OUPERSIST
        i = ck2.indexOf("OUPERSIST=");
        if (i >= 0) {
            i += 10;
            var ouper = ck2.substr(i, ck2.indexOf(";", i) - i) + "&";
            i = ouper.indexOf("CustomerState=");
            if (i > 0) {
                i += 14;
                ouper = ouper.substr(i, ouper.indexOf("&", i) - i);
                if (ouper == "Prospect") {
                    pg += "&ou_prospect_id=" + x;
                    types = "prospect-formal";
                    prospect = 1;
                }
                if (ouper == "Informal Prospect") {
                    pg += "&ou_prospect_id=" + x;
                    types = "prospect-informal";
                    prospect = 1;
                }
            }
        }

        if (prospect == 0) {
            pg += "&ou_student_id=" + x;
            types = "student";
        }
    }

    x = ou_getusertype(ck, "samsStaffID=");
    if (x != null) {
        pg += "&ou_staff_id=" + x;
        if (types.length > 0) types += ",";
        types += "staff";
    }

    x = ou_getusertype(ck, "samsTutorID=");
    if (x != null) {
        pg += "&ou_tutor_id=" + x;
        if (types.length > 0) types += ",";
        types += "tutor";
    }

    x = ou_getusertype(ck, "samsSelfRegID=");
    if (x != null) {
        pg += "&ou_selfreg_id=" + x;
        if (types.length > 0) types += ",";
        types += "self-registered";
    }

    x = ou_getusertype(ck, "samsCorporateID=");
    if (x != null) {
        pg += "&ou_corporate_id=" + x;
        if (types.length > 0) types += ",";
        types += "corporate";
    }

    x = ou_getusertype(ck, "samsVisitorID=");
    if (x != null) {
        pg += "&ou_special_access_id=" + x;
        if (types.length > 0) types += ",";
        types += "special-access";
    }

    if (types.length == 0) {
        pg += "&ou_unknown_id=1";
        types = "unknown";
    }

    pg += "&ou_visitor_types=" + types;

    return pg;
}

function ou_getusertype(ck, t) {
    var x1 = ck.indexOf(t);
    if (x1 <= 0) return null;
    x1 += t.length;
    return ck.substr(x1, ck.indexOf("&", x1) - x1);
}

/* To remove HTML tags and to replace it with ASCII */

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    alert(text);

}

/**
 * @deprecated since v1.0.1.38
 *
 * Converts the old click event into the new ouTrackLink, and reminds developers to update to the new version
 */
function ouClickEvent(obj, DAxParameters) {
    console.warn("Calling deprecated function - ouClickEvent. Please use ouTrackLink.");

    // Break the input string into key value pairs
    var params = {};
    DAxParameters.split('&').forEach(function (x) {
        var arr = x.split('=');
        arr[1] && (params[arr[0]] = arr[1]);
    });

    // Have a best guess at figuring out the name of this thing
    var linkName = null;
    try {
        // Use any innerHTML that might exist
        linkName = obj[0] == null ? obj.innerText : obj[0].innerText;
    }
    catch (err) {
        // If we couldnt grab an innerHTML build a name from the parameters the OU passes in
        linkName = params['ou_ev_pl'] + " - " + params['ou_ev_as'];
    }

    // Make a list of things we want to track
    var linkTrackVariables = Object.keys(params).join(',');

    ouTrackLink(obj, linkName, linkTrackVariables, params);
}

/**
 * Merges two objects into one
 * @param {*} target
 * @param {*} src
 */
function ouExtend(target, src) {
    for (var key in src) {
        if (src.hasOwnProperty(key)) target[key] = src[key];
    }
    return target;
}

/**
 * wait until a global asset is of a certain type.
 * @param {*} assetName = string name of asset to be checked
 * @param {*} assetType = type to compare to
 * @param {*} callback = function to call after the process
 */
function waitUntilTypeOf(assetName, assetType, callback) {
    // Check type in window is equal to the assetType passed
    if (typeof window[assetName] === assetType) {
        // If success check callback is a function then call it
        if (typeof callback === "function")
            callback()
    } else {
        // If failed then wait 1 second then try again
        setTimeout(function () {
            waitUntilTypeOf(assetName, assetType, callback)
        }, 1000)
    }
}


/**
 * Send tracking request to DTM.
 * If the incoming element (in obj) has a class of "DTM-test" then ouValidateTrackedLink is called
 * @param {*} obj
 * @param {*} LinkName
 * @param {*} LinkTrackVariables
 * @param {*} LinkTrackObject
 */
function ouTrackLink(obj, LinkName, LinkTrackVariables, LinkTrackObject) {
    waitUntilTypeOf('s_gi', 'function', function () {
        // Create the DTM object with our data
        var s = s_gi(isLive() ? 'openuniprod' : 'openunidev');
        s.linkTrackVars = LinkTrackVariables;
        s = ouExtend(s, LinkTrackObject);

        // If we are debugging, call the debug function
        var doneAction = null;
        if (ou_checkClass(obj, "DTM-test")) {
            doneAction = function () { ouValidateTrackedLink(obj, LinkName); };
        }

        // GO DTM!
        s.tl(obj, 'o', LinkName, null, doneAction);
    });
}

/**
 * A function allowing us to test that calls to DTM are firing
 * Calling this method puts a div at the bottom of the page body
 * The idea is that only ouTrackLink call this function.
 */
function ouValidateTrackedLink(obj, LinkName) {
    //obj.innerHTML += "!";
    var elemDiv = document.createElement('div');
    elemDiv.id = "dtm-tracking-confirmation";
    elemDiv.innerHTML = "Adobe DTM callback triggered successfully - " + LinkName;
    document.body.appendChild(elemDiv);
}

var ouinitdone = false;
var ousrchclk = 0;


function ou_init() {
    // Some legacy sites will call this function twice. Make sure we bail if we have already run
    if (ouinitdone) return;
    ouinitdone = true;

    // Make sure there is a sign in area to work on
    if (navigator.appName == "Netscape" && parseFloat(navigator.appVersion) < 5) return;

    document.getElementById("ou-copyright").style.display = "block";
    // Replace the copyright year with the current year.
    var today = new Date();
    if (document.getElementById("ou-copyright-year") != null)
        document.getElementById("ou-copyright-year").innerHTML = today.getFullYear();

    // Add the current FCA message
    loadFooterTextAsync();
    hide_toggle_menu();
    highlightInternational();
    // Listen out for requests to toggle the mobile menu
    addCompatibleListener(document.getElementById("ou-mobile-menu-toggle"), "click", toggleMobileMenu);

    // Listen out for requests to toggle the student footer elements
    addStudentFooterListeners();

    // Make sure there is a sign in area to work on before we start on the cookies
    if (document.getElementById("ou-signin1") == null) return;

    // listen for keypresses incase the search form cant be added to the DOM
    hookSearchBox();

    // Force the page to consider the current screen size
    onResizeEvent();

    cookies = document.cookie + ";";

    // Replace the sign in link
    samsSessionCookie = cookies.indexOf("SAMS2session=");
    if (samsSessionCookie < 0) {
        ele = document.getElementById("ou-signin2");
        ele.href = ele.href + "?nsh=2&URL=" + document.location.href;
        ou_setElementVisiblityByID("ou-identity", false);
        return;
    }
    // Remove the sams info from the rest of the cookie data
    samsSessionCookie += 13;
    i = cookies.indexOf(";", samsSessionCookie);
    samsCookieData = cookies.substr(samsSessionCookie, i - samsSessionCookie) + "&";

    // Change the sign in link to sign out.
    ou_setElementVisiblityByID("ou-signin1", false);
    ou_setElementVisiblityByID("ou-signout", true);


    // Display the users name
    nameCookie = cookies.indexOf("HS7BDF=");
    if (nameCookie >= 0) {
        nameCookie += 7;
        i = cookies.indexOf(";", nameCookie);
        Username = cookies.substr(nameCookie, i - nameCookie);
        i = Username.indexOf("\\");
        if (i >= 0) Username = Usernamesubstr(0, i);

        var uName = escapeHtml(Username);

        eleUserName = ou_GetElementsByClassName('ou-identity-name');
        for (var i = 0; i < eleUserName.length; ++i) {
            var item = eleUserName[i];
            item.innerText = uName;
        }


        // Show the users PI if they are a student
        var userID = ou_getusertype(samsCookieData, "samsStudentPI=");
        if (userID != null) {
            eleUserID = document.getElementById("ou-identity-id");
            if (eleUserID) {
                // userID contains the ID plus the rest of the cookie, so truncate it to get just the ID
                var uId = escapeHtml(userID);
                eleUserID.innerText = "(" + uId + ")";
            }
        } else {
            ou_setElementVisiblityByID("ou-identity-id", false);
        }

    }

    // Determine our user type
    userType = GetKeyValue(ou_usertype(""), "ou_visitor_types");

    // If we determined a prospect, use it
    if (userType.indexOf("prospect-formal") != -1 || userType.indexOf("prospect-informal") != -1) {
        ou_setElementVisiblityByID('ou-myaccount', true);
    }
    // Otherwise figure out what else to display
    else if (ou_usertype_check("samsStudentPI")) {
        ou_setElementVisiblityByID("ou-studenthome", true);
    } else if (ou_usertype_check("samsStaffID") || ou_usertype_check("samsTutorID")) {
        ou_setElementVisiblityByID("ou-studenthome", true);
        ou_setElementVisiblityByID("ou-intranethome", true);
        ou_setElementVisiblityByID("ou-tutorhome", true);

    }
    if (navigator.userAgent.indexOf('MSIE') !== -1 || navigator.appVersion.indexOf('Trident/') > 0) {
        var evt = document.createEvent('UIEvents');
        evt.initUIEvent('resize', true, false, window, 0);
        window.dispatchEvent(evt);
    } else {
        window.dispatchEvent(new Event('resize'));
    }

}

function hide_toggle_menu() {

    var x = document.getElementById("ou-ia-nav");
    var z = document.getElementById("ou-service-links");
    var a = document.getElementById("ou-header-nav");
    if ((x == null || window.getComputedStyle(x).display === "none") && (z == null || window.getComputedStyle(z).display === "none")) {
        var y = document.getElementById("ou-mobile-menu-toggle");
        y.style.display = "none";
    }
}
function ou_add_portallink(ele_ul, t, u) {
    ele_li = document.createElement("li");
    ele_a = document.createElement("a");
    ele_a.appendChild(document.createTextNode(t));
    ele_a.setAttribute("href", u);
    ele_li.appendChild(ele_a);
    ele_ul.appendChild(ele_li);
}

function ou_srchclk() {
    if (ousrchclk == 0) {
        document.getElementById("ousrch").value = "";
        ousrchclk = 1;
    }
}

function ou_mobile() {
    ou_killcookie("OUFULLSIZE");
    ou_setcookie("OUMOBILE", "1");
    location.reload(true);
}

function ou_desktop() {
    ou_killcookie("OUMOBILE");
    ou_setcookie("OUFULLSIZE", "M");
    location.reload(true);
}

function ou_killcookie(n) {
    document.cookie = n + "=;path=/;domain=.open.ac.uk;expires=Sun, 13 Dec 2009 12:01:01 GMT";
}

function ou_setcookie(n, v) {
    document.cookie = n + "=" + v + ";path=/;domain=.open.ac.uk;expires=Thu, 31 Dec 2099 23:59:59 GMT";
}

function ou_usertype_check(inType) {
    if (samsCookieData.indexOf(inType + "=") > 0)
        return true;

    return false;
}

// determines if a given id has a class
function ou_checkClass(ele, theClass) {
    if (ele != null) {
        var reg = new RegExp('(\\s|^)' + theClass + '(\\s|$)');
        var res = reg.test(ele.className);

        return res;
    }

    return false;
}

// Adds or removes a class from a node with the given elementID
function ou_setClass(ele, theClass, insert) {

    if (ele == null)
        return;

    if (insert == true) {
        ele.className += ele.className ? ' ' + theClass : theClass;
    }
    else {
        var reg = new RegExp('(\\s|^)' + theClass + '(\\s|$)');
        ele.className = ele.className.replace(reg, ' ');
    }
}

// Switches a given elements visibility
function ou_setElementVisiblityByID(elementID, visible) {
    ou_setClass(document.getElementById(elementID), 'ou-header-remove', !visible);
}


/* To support browsers older than IE 9 */
function ou_GetElementsByClassName(ClassName) {
    if (!document.getElementsByClassName) {
        var allT = document.getElementsByTagName('*'), allCN = [], i = 0, a;
        while (a = allT[i++]) {
            a.className == ClassName ? allCN[allCN.length] = a : null;
        }
        return allCN;
    }
    else {
        return document.getElementsByClassName(ClassName);
    }
}

/* Get the data from a key/value pair string */
function GetKeyValue(SearchString, KeyName) {
    var KeyValues = SearchString.split('&');
    for (var i = 0; i < KeyValues.length; i++) {
        var KeyValuePair = KeyValues[i].split('=');
        if (KeyValuePair[0] == KeyName) {
            return KeyValuePair[1];
        }
    }
}

function getEnv() {
    var a = document.createElement('a');
    a.href = window.location;

    if (a.hostname.indexOf('acct') != -1) {
        return 'acct';
    } else if (a.hostname.indexOf('dev') != -1) {
        return 'dev';
    } else if (a.hostname.indexOf('test') != -1 ||
        a.hostname.indexOf('-tst') != -1 ||
        a.hostname.indexOf('learn2syst') != -1 ||
        a.hostname.indexOf('localhost') != -1) {
        return 'test';
    } else {
        return 'live';
    }
}

function changeDTMScriptSource() {
    var env = getEnv();

    var script = document.createElement('script');

    if (env == "dev") {

        script.src = "https://assets.adobedtm.com/83c7b58f0b29/66882c504e10/launch-433232d3a1ab-development.min.js";
        script.async = true;
        document.head.appendChild(script);
    }
    else if (env == "test") {
        script.src = "https://assets.adobedtm.com/83c7b58f0b29/66882c504e10/launch-433232d3a1ab-development.min.js";
        script.async = true;
        document.head.appendChild(script);
    }
    else if (env == "acct") {
        script.src = "https://assets.adobedtm.com/83c7b58f0b29/66882c504e10/launch-277f28ee46b4-staging.min.js";
        script.async = true;
        document.head.appendChild(script);

    }
    else if (env == "live") {
        script.src = "https://assets.adobedtm.com/83c7b58f0b29/66882c504e10/launch-3cf91248ece2.min.js";
        script.async = true;
        document.head.appendChild(script);

    }


}

function loadCookieWidgetJS(callback) {
    var env = getEnv();
    var script = document.createElement('script');

    if (env == "dev" || env == "test" || env == "acct") {
        script.src = "https://cscript-cdn-irl-uat.cassiecloud.com/loader.js";
    }
    else if (env == "live") {
        script.src = "https://cscript-cdn-irl.cassiecloud.com/loader.js";
    }

    script.onreadystatechange = callback;
    script.onload = callback;
    document.head.appendChild(script);
}

function loadCookieWidget() {
    var env = getEnv();

    if (env == "dev" || env == "test" || env == "acct") {
        var cassieSettings = {
            widgetProfileId: 13,
            languageCode: "",
            licenseKey: "D5AAD677-E70E-41F5-80A3-846EFFFCD922",
            region: "irl",
            environment: "uat"
        };

        // Don't load cookie pop-up in ou study app
        if (!navigator.userAgent.toLowerCase().includes('moodlemobile')) {
            window.CassieWidgetLoader = new CassieWidgetLoaderModule(cassieSettings);
            focusCookieBannerOne();
        }
    }
    else if (env == "live") {
        var cassieSettings = {
            widgetProfileId: 1,
            languageCode: "",
            licenseKey: "E5C43C03-1803-4AA5-99AD-16D40EAF2622",
            region: "irl",
            environment: "production"
        };

        // Don't load cookie pop-up in ou study app
        if (!navigator.userAgent.toLowerCase().includes('moodlemobile')) {
            window.CassieWidgetLoader = new CassieWidgetLoaderModule(cassieSettings);
            focusCookieBannerOne();
        }
    }
}

function cookieBannerAccessbilitySetInterval() {
    var count = 0;
    var msg = setInterval(function () {
        if (++count > 3)
            clearInterval(msg);
        else {
            cookieBannerAccessibility();
        }
    },
        1000);

};

// Called from footer link
function managePreferenceSetInterval() {
    var count = 0;
    var msg = setInterval(function () {
        if (++count > 2)
            clearInterval(msg);
        else {
            // document.querySelector('.cassie-cookie-modal--footer-image--container').remove();
            document.addEventListener("focusin", function (event) {
                if (document.getElementById("cassie_accept_all_toggle_switch")) {
                    document.getElementById("cassie_accept_all_toggle_switch").setAttribute("tabIndex", "0");
                    document.getElementById("cassie_accept_all_toggle_switch").focus();
                }
                event.preventDefault();
            });

            if (document.getElementById("cassie-widget")) {
                document.getElementById("cassie-widget").addEventListener("focusin", function (e) {
                    e.stopPropagation();
                });
            }
        }
    },
        1000);
};

// Start Fix for cookie compliance accessbility issues

function cookieBannerAccessibility() {
    // Disable tab index for titles in popup 2
    var env = getEnv();
    if (document.getElementById("cassie_expand_strictly_necessary")) {
        document.getElementById("cassie_expand_strictly_necessary").setAttribute("tabIndex", "-1");
    }

    if (env == "dev" || env == "test" || env == "acct") {
        if (document.getElementById("cassie_expand_cookies_container_63")) {
            document.getElementById("cassie_expand_cookies_container_63").setAttribute("tabIndex", "-1");
        }
        if (document.getElementById("cassie_expand_cookies_container_64")) {
            document.getElementById("cassie_expand_cookies_container_64").setAttribute("tabIndex", "-1");
        }
        if (document.getElementById("cassie_expand_cookies_container_65")) {
            document.getElementById("cassie_expand_cookies_container_65").setAttribute("tabIndex", "-1");
        }
    }
    else if (env == "live") {
        if (document.getElementById("cassie_expand_cookies_container_14")) {
            document.getElementById("cassie_expand_cookies_container_14").setAttribute("tabIndex", "-1");
        }
        if (document.getElementById("cassie_expand_cookies_container_12")) {
            document.getElementById("cassie_expand_cookies_container_12").setAttribute("tabIndex", "-1");
        }
        if (document.getElementById("cassie_expand_cookies_container_13")) {
            document.getElementById("cassie_expand_cookies_container_13").setAttribute("tabIndex", "-1");
        }
    }
}

function focusCookieBannerOne() {
    var count = 0;
    var msg = setInterval(function () {
        if (++count > 4)
            clearInterval(msg);
        else {
            if (document.getElementById("popup-country-list") == null) {
                document.addEventListener("focusin", function (event) {
                    document.getElementById("cassie_accept_all_pre_banner").setAttribute("tabIndex", "0");
                    document.getElementById("cassie_accept_all_pre_banner").focus();
                    event.preventDefault();
                });

                if (document.getElementById("cassie-widget")) {
                    document.getElementById("cassie-widget").addEventListener("focusin", function (e) {
                        e.stopPropagation();
                    });
                }
            }
        }
    },
        1000);
}

function focusCookieBanner() {
    var count = 0;
    var msg = setInterval(function () {
        if (++count > 2)
            clearInterval(msg);
        else {
            if (document.getElementById("popup-country-list") == null) {
                // document.querySelector('.cassie-cookie-modal--footer-image--container').remove();
                var managePreferenceButton = document.getElementById("cassie_view_all_pre_banner");
                if (managePreferenceButton != null) {
                    managePreferenceButton.closest('button').addEventListener("click", function (event) {
                        document.addEventListener("focusin", function (event) {
                            if (document.getElementById("cassie_accept_all_toggle_switch")) {
                                document.getElementById("cassie_accept_all_toggle_switch").setAttribute("tabIndex", "0");
                                document.getElementById("cassie_accept_all_toggle_switch").focus();
                            }
                            event.preventDefault();
                        });
                    });
                    if (document.getElementById("cassie-widget")) {
                        document.getElementById("cassie-widget").addEventListener("focusin", function (e) {
                            e.stopPropagation();
                        });
                    }
                }
            }
        }
    },
        1000);
}
// End Fix for cookie compliance accessbility issues

function getEnvDelimiter(url) {
    var a = document.createElement('a');
    a.href = url;

    var periodLocation = a.hostname.indexOf('.');
    var subdomain = "";
    if (periodLocation != -1) {
        subdomain = a.hostname.substring(0, periodLocation);
    }

    if (subdomain.indexOf('learn') != -1) {
        return '';
    } else {
        return '-';
    }

}


function isLive() {
    return (getEnv() == 'live');
}


function changeLinks() {
    var env = getEnv();
    var delimiter = getEnvDelimiter();
    if (env != 'live') {
        var linkids = ['ou-logo', 'ou-ia-nav', 'ou-service-links', 'ou-org-footer', 'ou-mob-nav-logo', 'ou-mob-nav-service-links', 'ou-mob-nav-wrap'];
        var attr = 'href';
        var logoLinkId = ['ou-logo', 'ou-mob-nav-logo'];
        var voidHref = 'javascript:void(0);';
        var linkidsLength = linkids.length;
        for (var i = 0; i < linkidsLength; i++) {
            var section = document.getElementById(linkids[i]);
            if (section) {
                var elems = section.getElementsByTagName('a');
                for (var j = 0; j < elems.length; j++) {
                    var hreflink = elems[j].getAttribute(attr);
                    if ((hreflink != null && hreflink != undefined) && hreflink.indexOf('.open.') != -1 && hreflink !== "http://www2.open.ac.uk/students/charter") {
                        if ((env == 'test' || env == 'dev') && (logoLinkId.indexOf(linkids[i]) > -1) && hreflink != voidHref) {
                            devtestLogoUrl = 'https://web-dev-test1/ouhome/';
                            elems[j].setAttribute(attr, devtestLogoUrl);
                        }
                        else {
                            elems[j].setAttribute(attr, elems[j].getAttribute(attr).replace('.open.', getEnvDelimiter(hreflink) + env + '.open.'));
                        }
                    }
                    if ((hreflink != null && hreflink != undefined) && hreflink.indexOf('.openuniversity.edu') != -1) {
                        var elementLink = document.createElement('a');
                        elementLink.href = hreflink;
                        var urlValue = elementLink.href;
                        if (elementLink.protocol == 'https:') {
                            var replaceval = urlValue.replace("https://", "http://");
                            elems[j].setAttribute(attr, replaceval);
                            urlValue = elems[j].getAttribute(attr);
                        }
                        if (env == 'test') {
                            elems[j].setAttribute(attr, elems[j].getAttribute(attr).replace('.openuniversity.edu', getEnvDelimiter(urlValue) + 'test-kentico' + '.openuniversity.edu'));
                        }
                        else {
                            elems[j].setAttribute(attr, elems[j].getAttribute(attr).replace('.openuniversity.edu', getEnvDelimiter(urlValue) + env + '.openuniversity.edu'));
                        }
                    }
                }
            }
        }
    }

}

function addStudentFooterListeners() {
    eleCollapsible = ou_GetElementsByClassName('ou-collapsible-footer');
    for (var i = 0; i < eleCollapsible.length; ++i) {
        var item = eleCollapsible[i];
        addCompatibleListener(item, "click", toggleFooterMenu);
        addCompatibleListener(item, "keypress", activateFooterMenu);
    }

    addCompatibleListener(window, "resize", onResizeEvent);
}

function addCompatibleListener(eleToggle, event, targetFunction) {
    eleToggle.addEventListener ? eleToggle.addEventListener(event, targetFunction) : eleToggle.attachEvent(event, targetFunction);
}

function toggleMobileMenu() {
    var className = "ou-toggle";

    // Hide the content
    ele = document.getElementById("ou-header-nav");
    ou_setClass(ele, className, !ou_checkClass(ele, className));

    // Switch the toggle icon
    ele = document.getElementById("ou-mobile-menu-toggle");
    ou_setClass(ele, className, !ou_checkClass(ele, className));

}

function toggleFooterMenu(e) {

    // Switch the toggle icon
    ele = this.children[1];
    state = !ou_checkClass(ele, "ou-toggle");
    ou_setClass(ele, "ou-toggle", state);
    this.setAttribute('aria-selected', state);
    this.setAttribute('aria-expanded', state);

    // Toggle the content
    ele = this.nextElementSibling;
    state = !ou_checkClass(ele, "ou-mobile-menu-toggle");
    ou_setClass(ele, "ou-mobile-menu-toggle", state);
    ele.setAttribute('aria-hidden', state);
}

function activateFooterMenu(e) {

    var keyCode = e.keyCode || e.which;
    if (keyCode == '13' || keyCode == '32') {
        this.click();
    }
}

function onResizeEvent() {

    eleCollapsible = ou_GetElementsByClassName('ou-collapsible-footer');

    var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;

    var desiredIndex = (width > 767) ? -1 : 0;

    if (eleCollapsible[0] != null && eleCollapsible[0].tabIndex != desiredIndex) {
        for (var i = 0; i < eleCollapsible.length; ++i) {
            eleCollapsible[i].tabIndex = desiredIndex;
            if (desiredIndex == -1) {
                eleCollapsible[i].removeAttribute("aria-expanded");
                eleCollapsible[i].removeAttribute("aria-selected");
            }
            else {
                state = ou_checkClass(eleCollapsible[i], "ou-toggle");
                eleCollapsible[i].setAttribute("aria-expanded", state);
                eleCollapsible[i].setAttribute("aria-selected", state);
            }
        }
        //US-590505_OU_Public_Footer_Oct22:na5649
        //var myElm = document.querySelector(".ou-ia-footer");
        //if (myElm != null) {
        //    document.getElementsByClassName("ou-crest")[0].style.display = "block";
        //}
    }

    if (desiredIndex == -1) {
        hideOuHeader();
    }
}


function searchEnter(event) {
    if (event.which == 13 || event.keyCode == 13) {
        ou_search();
        return false;
    }
    return true;
}

function loadFooterTextAsync() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', document.querySelector('html').getAttribute('data-content_root') + 'ouheaders/ou-royal-fca-statement.txt', true);
    xhr.onreadystatechange = function () {
        if (this.readyState !== 4) return;
        if (this.status !== 200) return;

        document.getElementById('ou-footer-statement').innerHTML = this.responseText;
        OULanguageTranslation.init(document.getElementById('ou-footer-statement'));

        // // Translate the text if necessary, then display it
        // var translateObject = { originalText:this.responseText, translatedText:this.responseText, warning:false };
        // if (ouTranslateText(translateObject)) {
        // 	// Either we need to display this tranlation, or ouTranslateText flagged that we need to display a warning
        // 	if (document.body.className.indexOf("cymraeg") >= 0 || !isLive() && translateObject.warning == true) {
        // 		// Either we need to display this tranlation, or ouTranslateText flagged that we need to display a warning
        // 		document.getElementById('ou-footer-statement').innerHTML = translateObject.translatedText;
        // 	}
        // 	else {
        // 		// Either we need to display this tranlation, or ouTranslateText flagged that we need to display a warning
        // 		document.getElementById('ou-footer-statement').innerHTML = translateObject.originalText;
        // 	}
        // }
    };
    xhr.send();
}

//// A way to post without a form being available (*cough*kentico*cough*)
function submitSearch(elementID) {
    var href = "";
    switch (elementID) {
        case "ou-header-search-international":
            var env = getEnv();
            if (env == "test") {
                href = 'http://sttc-web-test.open.ac.uk/search/search-isw.shtml?q='
            }
            if (env == "acct") {
                href = 'https://search-acct.open.ac.uk/search/search-isw.shtml?q='
            }
            if (env == "live") {
                href = 'https://search.open.ac.uk/search/search-isw.shtml?q=';
            }
            break;
        case "ou-header-search-openlearn":
            href = 'http://search.open.ac.uk/openlearn/search/results?q='
            break;
        default:
            var env = getEnv();
            if (env == "dev") {
                href = 'http://sttc-web-test.open.ac.uk/search/search.shtml?q='
            }
            if (env == "test") {
                href = 'http://sttc-web-test.open.ac.uk/search/search.shtml?q='
            }
            if (env == "acct") {
                href = 'https://search-acct.open.ac.uk/search/search.shtml?q='
            }
            if (env == "live") {
                href = 'https://search.open.ac.uk/search/search.shtml?q='
            }
            break;
    }
    var headerSearchVal = document.getElementById(elementID);
    if (href && headerSearchVal.value) {
        window.location.href = href + headerSearchVal.value;
    }
    return false;
}

function hookSearchBox() {
    // Hook the key press events if we dont have a search form
    var oFormTest = document.getElementById("ou-search");
    if (oFormTest == null) {

        eleSearchBoxes = ou_GetElementsByClassName('ou-header-search');
        for (var i = 0; i < eleSearchBoxes.length; ++i) {
            var item = eleSearchBoxes[i];
            item.onkeypress = function (e) {
                if (!e) e = window.event;
                var keyCode = e.keyCode || e.which;
                if (keyCode == '13') {
                    // Enter pressed

                    // Stop this bubbling up to any parent forms and submitting them
                    event.preventDefault ? event.preventDefault() : event.returnValue = false;
                    submitSearch(this.id);
                    return false;
                }
            }
        }

    }
}


function onSearchBoxInput(e) {
    if (!e) e = window.event;
    var keyCode = e.keyCode || e.which;
    if (keyCode == '13') {
        // Enter pressed
        var target = e.target || e.srcElement;

        // Stop this bubbling up to any parent forms and submitting them
        e.preventDefault ? e.preventDefault() : e.returnValue = false;
        submitSearch(target.id);
    }
}

function skipToContent(event) {
    var element = document.getElementById(location.hash.substring(1));
    if (element) {
        // If the target isnt a tabable item, use tabIndex to allow us to focus there.
        if (!/^(?:a|select|input|button|textarea)$/i.test(element.tagName)) {
            element.tabIndex = -1;
        }
        // Set the tab position to this item
        element.focus();
    }
}


function contactTheOULink() {
    // Get value of SAMS2session cookie
    var cookieValue = document.cookie + ";";
    var i = cookieValue.indexOf("SAMS2session=");
    var publicElement = document.getElementById("ou-public-contact");


    if (i < 0) {
        publicElement.href = "https://www.open.ac.uk/contact/";
    }
    else {

        var studentElement = document.getElementById("ou-student-contact");
        var tutorElement = document.getElementById("ou-tutor-contact");
        var userType = GetKeyValue(ou_usertype(""), "ou_visitor_types");


        if (userType.indexOf("prospect-formal") != -1 || userType.indexOf("prospect-informal") != -1) {
            studentElement.href = "https://www.open.ac.uk/contact/";
            tutorElement.href = "https://www.open.ac.uk/contact/";
            publicElement.href = "https://www.open.ac.uk/contact/";
        }
        else if (ou_usertype_check("samsTutorID")) {
            studentElement.href = "https://www2.open.ac.uk/tutors/help/who-to-contact/";
            tutorElement.href = "https://www2.open.ac.uk/tutors/help/who-to-contact/";
            publicElement.href = "https://www2.open.ac.uk/tutors/help/who-to-contact/";
        }
        else if (ou_usertype_check("samsStudentPI")) {
            studentElement.href = "https://help.open.ac.uk/contact/";
            tutorElement.href = "https://help.open.ac.uk/contact/";
            publicElement.href = "https://help.open.ac.uk/contact/";
        } else if (ou_usertype_check("samsStaffID")) {
            studentElement.href = "https://help.open.ac.uk/contact/";
            tutorElement.href = "https://help.open.ac.uk/contact/";
            publicElement.href = "https://help.open.ac.uk/contact/";
        }

        else {
            studentElement.href = "https://www.open.ac.uk/contact/";
            tutorElement.href = "https://www.open.ac.uk/contact/";
            publicElement.href = "https://www.open.ac.uk/contact/";
        }
    }

}


function footerContactTheOULink() {


    var footerStudentElement = document.getElementById("ou-footer-student-contact");
    var footerStudentElement1 = document.getElementById("ou-footer-student-contact1");
    var footerTutorElement = document.getElementById("ou-footer-tutor-contact");
    var footerPublicElement = document.getElementById("ou-footer-public-contact");

    // Get value of SAMS2session cookie
    var cookieValue = document.cookie + ";";
    var i = cookieValue.indexOf("SAMS2session=");

    if (i < 0) {
        if (footerPublicElement != null) {
            footerPublicElement.href = "https://www.open.ac.uk/contact";
        }
    }
    else {
        var userType = GetKeyValue(ou_usertype(""), "ou_visitor_types");

        if (userType.indexOf("prospect-formal") != -1 || userType.indexOf("prospect-informal") != -1) {
            if (footerStudentElement != null) {
                footerStudentElement.href = "https://www.open.ac.uk/contact";
            }
            if (footerStudentElement1 != null) {
                footerStudentElement1.href = "https://www.open.ac.uk/contact";
            }
            if (footerTutorElement != null) {
                footerTutorElement.href = "https://www.open.ac.uk/contact";

            }
            if (footerPublicElement != null) {
                footerPublicElement.href = "https://www.open.ac.uk/contact";

            }
        }
        else if (ou_usertype_check("samsTutorID")) {
            if (footerStudentElement != null) {
                footerStudentElement.href = "https://www2.open.ac.uk/tutors/help/who-to-contact/";
            }
            if (footerStudentElement1 != null) {
                footerStudentElement1.href = "https://www2.open.ac.uk/tutors/help/who-to-contact/";
            }
            if (footerTutorElement != null) {
                footerTutorElement.href = "https://www2.open.ac.uk/tutors/help/who-to-contact/";

            }
            if (footerPublicElement != null) {
                footerPublicElement.href = "https://www2.open.ac.uk/tutors/help/who-to-contact/";

            }
        }
        else if (ou_usertype_check("samsStudentPI")) {
            if (footerStudentElement != null) {
                footerStudentElement.href = "https://help.open.ac.uk/contact/";
            }
            if (footerStudentElement1 != null) {
                footerStudentElement1.href = "https://help.open.ac.uk/contact/";
            }
            if (footerTutorElement != null) {
                footerTutorElement.href = "https://help.open.ac.uk/contact/";

            }
            if (footerPublicElement != null) {
                footerPublicElement.href = "https://help.open.ac.uk/contact/";

            }
        }

        else if (ou_usertype_check("samsStaffID")) {
            if (footerStudentElement != null) {
                footerStudentElement.href = "https://help.open.ac.uk/contact/";
            }
            if (footerStudentElement1 != null) {
                footerStudentElement1.href = "https://help.open.ac.uk/contact/";
            }
            if (footerTutorElement != null) {
                footerTutorElement.href = "https://help.open.ac.uk/contact/";

            }
            if (footerPublicElement != null) {
                footerPublicElement.href = "https://help.open.ac.uk/contact/";

            }
        }
        else {
            if (footerStudentElement != null) {
                footerStudentElement.href = "https://www.open.ac.uk/contact";
            }
            if (footerStudentElement1 != null) {
                footerStudentElement1.href = "https://www.open.ac.uk/contact";
            }
            if (footerTutorElement != null) {
                footerTutorElement.href = "https://www.open.ac.uk/contact";

            }
            if (footerPublicElement != null) {
                footerPublicElement.href = "https://www.open.ac.uk/contact";

            }
        }

    }


}


var count = 0;
function spacerImage() {
    var msg = setInterval(function () {
        if (++count > 5)
            clearInterval(msg);
        else {
            addAltToSpacerImage();
        }
    },
        1000);

};

function addAltToSpacerImage() {
    if (document.querySelectorAll("img[src*='secure.adnxs']").length !== 0)
        document.querySelectorAll("img[src*='secure.adnxs']")[0].alt = '';
    if (document.querySelectorAll("img[src*='doubleclick']").length !== 0)
        document.querySelectorAll("img[src*='doubleclick']")[0].alt = '';
}

function zoomResizeInFooter() {

    var browserZoomLevel = window.devicePixelRatio * 100;
    if (navigator.userAgent.indexOf("Firefox") != -1 && document.getElementById("ou-ia-public")) {
        document.getElementById('ou-ia-public').classList.add('ou-width100Footer');
        if (browserZoomLevel < 65 || browserZoomLevel > 70) {
            document.getElementById('ou-ia-public').classList.remove('ou-width100Footer');
        }
    }
}

function highlightInternational() {
    if (window.location.href.split("/").slice(-2)[0] == "courses" && window.location.href.split("/").slice(-2)[1] == "international-students") {
        document.body.className = document.body.className.replace("ou-ia-courses", "ou-ia-inter_national");
    }

}
//US-590505_OU_Public_Footer_Oct22:na5649
function hideOuHeader() {
    var myEle = document.querySelector(".ou-ia-footer");
    if (myEle != null) {
        document.getElementsByClassName("ou-crest")[0].style.display = "none";
    }
}

function searchfocus() {
    document.addEventListener("click", function (evt) {
        const flyoutEl = document.querySelector(".ou-header-search");
        var targetEl = evt.target; // clicked element
        do {
            if (targetEl == flyoutEl) {
                // This is a click inside, does nothing, just return.
                flyoutEl.classList.add("input-focus");
                return;
            }
            // Go up the DOM
            targetEl = targetEl.parentNode;
        } while (targetEl);
        // This is a click outside.
        flyoutEl.classList.remove("input-focus");
    });
}

window.addEventListener ? window.addEventListener("load", ou_init, false) : window.attachEvent && window.attachEvent("onload", ou_init);
window.addEventListener ? window.addEventListener("load", changeDTMScriptSource, false) : window.attachEvent && window.attachEvent("onload", changeDTMScriptSource);
window.addEventListener ? window.addEventListener("load", contactTheOULink, false) : window.attachEvent && window.attachEvent("onload", contactTheOULink);
window.addEventListener ? window.addEventListener("load", footerContactTheOULink, false) : window.attachEvent && window.attachEvent("onload", footerContactTheOULink);
window.addEventListener ? window.addEventListener("load", changeLinks, false) : window.attachEvent && window.attachEvent("onload", changeLinks);
window.addEventListener ? window.addEventListener("hashchange", skipToContent, false) : window.attachEvent && window.attachEvent("onhashchange", skipToContent);
window.addEventListener ? window.addEventListener("load", spacerImage, false) : window.attachEvent && window.attachEvent("onload", spacerImage);
window.addEventListener ? window.addEventListener("load", zoomResizeInFooter, false) : window.attachEvent && window.attachEvent("load", zoomResizeInFooter);
window.addEventListener ? window.addEventListener("resize", zoomResizeInFooter, false) : window.attachEvent && window.attachEvent("resize", zoomResizeInFooter);
window.addEventListener ? window.addEventListener("DOMContentLoaded", loadCookieWidgetJS(loadCookieWidget), false) : window.attachEvent && window.attachEvent("DOMContentLoaded", loadCookieWidgetJS(loadCookieWidget));
window.addEventListener ? window.addEventListener("DOMContentLoaded", focusCookieBanner, false) : window.attachEvent && window.attachEvent("DOMContentLoaded", focusCookieBanner);
window.addEventListener ? window.addEventListener("load", cookieBannerAccessbilitySetInterval, false) : window.attachEvent && window.attachEvent("onload", cookieBannerAccessbilitySetInterval);
//US-590505_OU_Public_Footer_Oct22:na5649
window.addEventListener ? window.addEventListener("DOMContentLoaded", hideOuHeader, false) : window.attachEvent && window.attachEvent("DOMContentLoaded", hideOuHeader);
//US-658981_Rebranding_H&F_Apr23-NA5649
window.addEventListener ? window.addEventListener("DOMContentLoaded", searchfocus, false) : window.attachEvent && window.attachEvent("DOMContentLoaded", searchfocus);
