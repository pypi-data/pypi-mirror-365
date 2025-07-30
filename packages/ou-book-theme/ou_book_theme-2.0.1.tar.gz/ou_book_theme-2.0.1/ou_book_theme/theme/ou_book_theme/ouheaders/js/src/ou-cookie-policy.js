var OUCookiePolicy = {

    getCookie: function() {
        return Cookie.get('ou_cookie_policy');
    },

    setCookie: function($value) {
        return Cookie.set('ou_cookie_policy', $value, 365);
    },
    accepted: function() {
        return (OUCookiePolicy.getCookie() == 'continue' ||
        Cookie.get('SAMSsession') != null ||
        Cookie.get('SAMS2session') != null
        );
    },

    getPolicyUrl: function() {
        var oudomain = window.location.hostname;
        var idx = oudomain.indexOf(".");
        var mdomain = oudomain.slice(idx, oudomain.length);
        return (mdomain == ".openuniversity.edu") ? '/privacy' : 'http://www.open.ac.uk/about/main/strategy-and-policies/policies-and-statements/cookie-use-ou-website';
    },


    displayNotification: function() {
        var cookieMessage = document.createElement("div");
        cookieMessage.setAttribute('class', 'ou-cookies-interaction');
        var containerDiv = document.createElement("div");
        containerDiv.setAttribute('class', 'ou-container');
        var rowDiv = document.createElement("div");
        rowDiv.setAttribute('class', 'ou-row');
        var infoText = document.createElement("h3");
        infoText.setAttribute('data-translate', 'true');
        infoText.setAttribute('id', 'ou-header-id1');
        var textNodeOne = document.createTextNode("Cookies on our website");
        infoText.appendChild(textNodeOne);
        rowDiv.appendChild(infoText);
        containerDiv.appendChild(rowDiv);
        cookieMessage.appendChild(containerDiv);
        OULanguageTranslation.init(infoText.id);
        var divWrap = document.createElement("div");
        divWrap.setAttribute('id', 'ou-polWrap');
        divWrap.setAttribute('class', 'ou-row ou-policyWrap');
        var paraTag = document.createElement("p");
        paraTag.setAttribute('data-translate', 'true');
        paraTag.setAttribute('id', 'ou-para-id');
        var textNodeTwo = document.createTextNode("We use cookies to make sure our websites work effectively and to improve your user experience.  If you continue to use this site we will assume that you are happy with this. However, you can change your cookie settings at any time. ");
        paraTag.appendChild(textNodeTwo);
        divWrap.appendChild(paraTag);
        rowDiv.appendChild(divWrap);
        containerDiv.appendChild(rowDiv);
        cookieMessage.appendChild(containerDiv);
        OULanguageTranslation.init(paraTag);
        var anchorTag = document.createElement("a");
        anchorTag.setAttribute('data-translate', 'true');
        anchorTag.setAttribute('href', OUCookiePolicy.getPolicyUrl());
        anchorTag.setAttribute('onclick', 'javaScript:document.location.href=OUCookiePolicy.getPolicyUrl()');
        anchorTag.setAttribute('class', 'cookieInfo');
        anchorTag.setAttribute('id', 'ou-anchortag-id1');
        var textNodeThree = document.createTextNode("More Info/Change Settings.");
        anchorTag.appendChild(textNodeThree);
        paraTag.appendChild(anchorTag);
        OULanguageTranslation.init(anchorTag);
        var anchorTag2 = document.createElement("a");
        anchorTag2.setAttribute('data-translate', 'true');
        anchorTag2.setAttribute('class', 'ou-button');
        anchorTag2.setAttribute('id', 'ou-cookies-bar-button');
        anchorTag2.setAttribute('role', 'button');
        anchorTag2.setAttribute('href', '#');
        anchorTag2.setAttribute('onclick', 'javaScript:OUCookiePolicy.accept()');
        var textNodeFour = document.createTextNode("Continue");
        anchorTag2.appendChild(textNodeFour);
        OULanguageTranslation.init(anchorTag2.id);
        divWrap.appendChild(anchorTag2);
        cookieWrapper = document.createElement('div');
        cookieWrapper.id = 'i-cookies-bar';
        cookieWrapper.className = 'ou-cookies-bar ou-active';
        cookieWrapper.appendChild(cookieMessage);
        document.body.insertBefore(cookieWrapper, document.body.firstChild);
        if (navigator.userAgent.indexOf('MSIE') !== -1 || navigator.appVersion.indexOf('Trident/') > 0) {
            $(window).trigger('resize');
        } else {
            window.dispatchEvent(new Event('resize'));
        }
     },


    accept: function() {
        OUCookiePolicy.setCookie('continue');
        //TG Ireland code starts here
        if (typeof countryCode !== 'undefined' && countryCode == '') {
            OUCookiePolicy.setCookie(countryCode);
        }
        //ends here

        // Get countryCode set by drupal sites inorder to set countrycode upon cookie accept
        if (typeof countryCode !== 'undefined' && countryCode != '') {
            OUCookiePolicy.setCookie(countryCode);
        }
        location.reload(true);
    },

    notify: function() {
        OUCookiePolicy.displayNotification();

        OUCookiePolicy.setCookie('notified');
    },


    init: function() {
        if(OUCookiePolicy.accepted()) return;

        OUCookiePolicy.notify();
    },
};

// https://developers.livechatinc.com/blog/setting-cookies-to-subdomains-in-javascript/
var Cookie = {
    set: function(name, value, days) {
        var domain, domainParts, date, expires, host;

        if (days) {
            date = new Date();
            date.setTime(date.getTime()+(days*24*60*60*1000));
            expires = "; expires="+date.toGMTString();
            } else {
            expires = "";
            }

        host = location.host;
        if (host.split('.').length === 1) {
            // no "." in a domain - it's localhost or something similar
            document.cookie = name+"="+value+expires+"; path=/";
            } else {
            // Remember the cookie on all subdomains.
            //
            // Start with trying to set cookie to the top domain.
            // (example: if user is on foo.com, try to set
            //  cookie to domain ".com")
            //
            // If the cookie will not be set, it means ".com"
            // is a top level domain and we need to
            // set the cookie to ".foo.com"
            domainParts = host.split('.');
            domainParts.shift();
            domain = '.'+domainParts.join('.');

            document.cookie = name+"="+value+expires+"; path=/; domain="+domain;

            // check if cookie was successfuly set to the given domain
            // (otherwise it was a Top-Level Domain)
            if (Cookie.get(name) == null || Cookie.get(name) != value) {
                // append "." to current domain
                domain = '.'+host;
                document.cookie = name+"="+value+expires+"; path=/; domain="+domain;
            }
        }
    },

    get: function(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for (var i=0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') {
                c = c.substring(1,c.length);
            }

            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
        }

        return null;
    },

    erase: function(name) {
        Cookie.set(name, '', -1);
    }
};

// Choose wheather to diplay cookie policy notification
// window.addEventListener ? window.addEventListener("load",OUCookiePolicy.init,false) : window.attachEvent && window.attachEvent("onload",OUCookiePolicy.init);