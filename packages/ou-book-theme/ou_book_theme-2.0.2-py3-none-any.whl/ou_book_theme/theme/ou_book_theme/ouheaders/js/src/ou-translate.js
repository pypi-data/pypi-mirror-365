// This has been set up in a language agnostic way, but to add more languages would
// need a way to load an object based on the document.documentElement.lang attribute.
function OULanguageTranslation() {

    this.requiresTranslation = false;

}

OULanguageTranslation.init = function(targetElement) {
    // If we werent passed a specific value to translate, find them all ourself.
    var workItems = (targetElement && targetElement.nodeType) ? targetElement : document.querySelectorAll("[data-translate]");

    if (document.documentElement.lang == "" && document.getElementsByTagName('html')[0].getAttribute('xml:lang') != "") {
        document.documentElement.lang = document.getElementsByTagName('html')[0].getAttribute('xml:lang');
    }

    // If the document contains a lang we know about then flag that we should do the translation
    if (document.documentElement.lang !== "") {
        this.requiresTranslation = document.documentElement.lang === "cy" ? true : false;

        // TODO: If we ever do more langauges, replace the cymraeg CSS class with cy in the LESS source
        var LanguageClass = "cymraeg"; // = document.body.className;
        if (this.requiresTranslation === true && (' ' + document.body.className + ' ').indexOf(" " + LanguageClass + " ") === -1)  {
            document.body.className += ' ' + LanguageClass; // Apply CSS relevant to this langauge
        }
    }

    if (this.requiresTranslation) {
        // Translate each element targeted with a [data-translate]
        if (workItems.constructor === NodeList) {
            for (var i = 0; i < workItems.length; i++){
                OULanguageTranslation.translate(workItems[i]);
            }
            // calling alphaorder function to convert undergraduate section into alphabetical order only in welsh footer
            alphaOrder();
        }
        else {
            OULanguageTranslation.translate(workItems);
        }
    }

};

OULanguageTranslation.translate = function(match) {

    var translateObject = new TranslationArea(match);
    // If we have a match, translate it
    if (translateObject.TranslateText()) {
        translateObject.setText();
    }
};

function TranslationArea(targetElement) {

    this.targetElement = targetElement;
    this.translatedText = "";
    this.warning = false;

    this.getText = function () {
        if (this.targetElement.nodeName === 'INPUT') {
            return this.targetElement.getAttribute("placeholder").trim();
        }
        else {
            return this.targetElement.innerHTML.trim();
        }
    };
    this.originalText = this.getText();

    this.setText = function () {
        if (this.targetElement.nodeName === 'INPUT') {
            this.targetElement.setAttribute("placeholder", this.translatedText);
        }
        else {
            this.targetElement.innerHTML = this.translatedText;
        }
    };

    this.TranslateText = function () {
        var warningMessage = " (missing welsh translation)";
        this.originalText = this.originalText.replace(warningMessage, "");
        var textKey = this.originalText.replace(/<[^>]+>/g, '').replace("&nbsp;", '').trim();
        this.translatedText = this.originalText.replace(textKey, _translations[textKey]);

        if (textKey in _translations) {
            return true;
        } else {
            if (!isLive()) { // Otherwise flag that we were asked to translate something with no translation (but not on live)
                this.translatedText = this.originalText + warningMessage;
                this.warning = true;
                return true;
            } else {
                this.translatedText = this.originalText;
                return false;
            }
        }
    };
}


if (typeof String.prototype.trim !== 'function') {
    String.prototype.trim = function () {
        if (this !== null) {
            return this.replace(/^\s+|\s+$/g, '');
        }
        return this;
    };
}

/* US-625794_footer Alphabetical order_Nov22: na5649 */
function sortList(ul) {
    var list, i, switching, b, shouldSwitch;
    list = document.getElementById(ul);
    switching = true;
    while (switching) {
        switching = false;
        b = list.getElementsByTagName("LI");
        for (i = 0; i < (b.length - 1); i++) {
            shouldSwitch = false;
            if (b[i].textContent > b[i + 1].textContent) {
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            b[i].parentNode.insertBefore(b[i + 1], b[i]);
            switching = true;
        }
    }
}

/* US-625794_footer Alphabetical order_Nov22: na5649 */
function alphaOrder() {
        sortList("ou-publicFooter-undergraduate");
}

// Start translation code after page is loaded
window.addEventListener ? window.addEventListener("load", OULanguageTranslation.init, false) : window.attachEvent && window.attachEvent("onload", OULanguageTranslation.init);

// Welsh Translations follow.
var _translations = {
	"The Open University": "Y Brifysgol Agored",
	'<i class="int-icon int-icon-arrow-circle-down">&nbsp;</i> Skip to content': '<i class="int-icon int-icon-arrow-circle-down">&nbsp;</i> Ymlaen i’r cynnwys',
	'<I class="int-icon int-icon-arrow-circle-down">&nbsp;</I>Skip to content': '<i class="int-icon int-icon-arrow-circle-down">&nbsp;</i> Ymlaen i’r cynnwys', // IE8 markup format
	"Skip to content": "Ymlaen i’r cynnwys",
	"Sign in": "Mewngofnodi",
	"Sign out": "Allgofnodi",
	"My Account": "Fy nghyfrif",
	"StudentHome": "HafanMyfyrwyr",
	"TutorHome": "HafanTiwtoriaid",
    "IntranetHome": "HafanMewnrwyd",
    "Accessibility": "Hygyrchedd",
	"Contact us": "Cysylltu &acirc; ni",
	"Search the OU": "Chwilio’r OU",
	"All rights reserved. The Open University is incorporated by Royal Charter (RC 000391), an exempt charity in England &amp; Wales and a charity registered in Scotland (SC 038302). The Open University is authorised and regulated by the Financial Conduct Authority in relation to its secondary activity of credit broking.":
		"Cedwir pob hawl. Mae’r Brifysgol Agored yn gorfforedig drwy Siarter Brenhinol (RC000391), yn elusen a eithrir yng Nghymru a Lloegr ac yn elusen gofrestredig yn yr Alban (SC038302). Awdurdodir a rheoleiddir y Brifysgol Agored gan yr Awdurdod Ymddygiad Ariannol o ran ei weithgarwch eilradd o froceru credyd. ",
	"Cookies on our website": "Cwcis ar ein gwefan",
	"We use cookies to make sure our websites work effectively and to improve your user experience.  If you continue to use this site we will assume that you are happy with this. However, you can change your cookie settings at any time.": "Rydym yn defnyddio cwcis i sicrhau bod ein gwefannau yn gweithio'n effeithiol ac i wella eich profiad fel defnyddiwr. Os byddwch yn parhau i ddefnyddio'r wefan, byddwn yn tybio eich bod yn fodlon gyda hyn. Fodd bynnag, gallwch newid eich gosodiadau cwcis unrhyw dro. ",
	"More Info/Change Settings.": "Mwy o wybodaeth/newid gosodiadau.",
    "Continue": "Parhau",
    //english to welsh lang. for new public-footer: na5649
    "Explore": "Archwilio",
    "Study with us": "Astudiwch gyda ni",
    "Supported distance learning": "Dysgu o bell sydd wedi'i gefnogi",
    "Funding your studies": "Ariannu eich astudiaethau",
    "International students": "Myfyrwyr rhyngwladol",
    "Global reputation": "Enw da byd-eang",
    "Business": "Busnes",
    "Apprenticeships": "Prentisiaethau",
    "Develop your workforce": "Datblygu eich gweithlu",
    "News &amp; media": "Newyddion a'r cyfryngau",
    "Jobs": "Swyddi",
    "Contact the OU": "Cysylltwch â'r Brifysgol Agored",
    "Undergraduate": "Israddedig",
    "Arts and Humanities": "Celfyddydau a Dyniaethau",
    "Art History": "Hanes Celf",
    "Biology": "Bioleg",
    "Business and Management": "Busnes a Rheolaeth",
    "Chemistry": "Cemeg",
    "Combined Studies": "Astudiaethau Cyfunol",
    "Computing and IT": "Cyfrifiadura a TG",
    "Counselling": "Cwnsela",
    "Creative Writing": "Ysgrifennu Creadigol",
    "Criminology": "Troseddeg",
    "Design": "Dylunio",
    "Early Years": "Blynyddoedd Cynnar",
    "Economics": "Economeg",
    "Education": "Addysg",
    "Electronic Engineering": "Peirianneg Electronig",
    "Engineering": "Peirianneg",
    "English": "Saesneg",
    "Environment": "Amgylchedd",
    "Film and Media": "Ffilm a'r Cyfryngau",
    "Geography": "Daearyddiaeth",
    "Health and Social Care": "Iechyd a Gofal Cymdeithasol",
    "Health and Wellbeing":	"Iechyd a Lles",
    "Health Sciences": "Gwyddorau Iechyd",
    "History": "Hanes",
    "International Studies": "Astudiaethau Rhyngwladol",
    "Languages": "Ieithoedd",
    "Law": "Cyfraith",
    "Marketing": "Marchnata",
    "Mathematics": "Mathemateg",
    "Mental Health": "Iechyd meddwl",
    "Music": "Cerddoriaeth",
    "Nursing and Healthcare": "Nyrsio a Gofal Iechyd",
    "Philosophy": "Athroniaeth",
    "Physics": "Ffiseg",
    "Politics":	"Gwleidyddiaeth",
    "Psychology": "Seicoleg",
    "Religious Studies": "Astudiaethau Crefyddol",
    "Science": "Gwyddoniaeth",
    "Social Sciences": "Gwyddorau Cymdeithasol",
    "Social Work": "Gwaith Cymdeithasol",
    "Sociology": "Cymdeithaseg",
    "Software Engineering":	"Peirianneg Meddalwedd",
    "Sport and Fitness": "Chwaraeon a Ffitrwydd",
    "Statistics": "Ystadegau",
    "Postgraduate":	"Ôl-raddedig",
    "Postgraduate study": "Astudiaeth ôl-raddedig",
    "Research degrees":	"Graddau ymchwil",
    "Masters in Art History (MA)": "Meistr mewn Hanes Celf (MA)",
    "Masters in Computing (MSc)": "Meistr mewn Cyfrifiadura (MSc)",
    "Masters in Creative Writing (MA)": "Meistr mewn Ysgrifennu Creadigol (MA)",
    "Masters degree in Education": "Gradd Meistr mewn Addysg",
    "Masters in Engineering (MSc)": "Meistr mewn Peirianneg (MSc)",
    "Masters in English Literature (MA)": "Meistr mewn Llenyddiaeth Saesneg (MA)",
    "Masters in History (MA)": "Meistr mewn Hanes (MA)",
    "Master of Laws (LLM)": "Meistr y Gyfraith (LLM)",
    "Masters in Mathematics (MSc)": "Meistr mewn Mathemateg (MSc)",
    "Masters in Psychology (MSc)": "Meistr mewn Seicoleg (MSc)",
    "A to Z of Masters degrees": "A i Y o raddau Meistr",
    "Policy": "Polisi",
    "Accessibility statement": "Datganiad Hygyrchedd",
    "Conditions of use": "Amodau defnyddio",
    "Privacy policy": "Polisi preifatrwydd",
    "Cookie policy": "Polisi cwcis",
    "Manage cookie preferences": "Rheoli dewisiadau cwcis",
    "Modern slavery act (pdf 149kb)": "Deddf caethwasiaeth fodern (pdf 149kb)",
    "Copyright": "Hawlfraint"
};