// Random one-liner hash function from https://stackoverflow.com/questions/6122571/simple-non-secure-hash-function-for-javascript
let hashJoaat=function(b){
    for(var a=0,c=b.length;c--;)a+=b.charCodeAt(c),a+=a<<10,a^=a>>6;a+=a<<3;a^=a>>11;return((a+(a<<15)&4294967295)>>>0).toString(16)
};


// We can't monitor browser requests over-the-wire, so we'll replicate them.
// If we're lucky, this will be cached!
function getAjax(url, success) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.onreadystatechange = function() {
	if (xhr.readyState>3 && xhr.status==200) success(xhr.responseText);
    };
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.send();
    return xhr;
}

// Set of things we've already logged
let logged = new Set();

// Listen for requests, and scarf down subtitle ones.
function listener(request) {
    // For debugging. This is a quick  hack. Remember?
    console.log(request);

    // These are the requests to YT and KA for subtitles. 
    if(request.url.includes("transcript") ||
       request.url.includes("timedtext")) {
	// Don't get into infinite loop; we only load transcripts once
	if(logged.has(request.url)) {
	    return;
	}
	logged.add(request.url);
	// We want to log the title. Navigating through the right
	// pages is important to make sure we have the right one.
	t = browser.tabs.get(request.tabId).then(function(tabobj) {
	    let title = tabobj.title;
	    getAjax(request.url, function(data) {
		// We add a bit of metadata, in case it's helpful later
		payload = JSON.stringify({
		    "data": data,
		    "url": request.url,
		    "originURL": request.originURL,
		    "ts": Date.now(),
		    "title": title});
		console.log(payload);
		// And we download to our downloads directory.
		// We'll clean these up with Python. See translate.py and
		// pretty_print.py
		let blob2 = new Blob([payload], {type : 'application/json'});
		console.log(request.url);
		console.log(blob2);
		let bloburi = URL.createObjectURL(blob2);
		browser.downloads.download({
		    url: bloburi,
		    filename: hashJoaat(request.url)+".json"
		});
	    });
	});
    }
    return {};
}

// Set up the listener
browser.webRequest.onBeforeRequest.addListener(
    listener,
    {urls: ["https://www.khanacademy.org/api/internal/videos/*",
	   "https://www.youtube-nocookie.com/api/*"]},
    ["requestBody"]
);

// So we can confirm we've loaded correctly.
console.log("Loaded");
