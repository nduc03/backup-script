// auto click and download non-downloadable Sharepoint (OneDrive) document pages as png (only works on some specific sites)
async function downloadPng(basename, startPage, endPage, sleepTimeMs) {
    if (startPage > endPage) {
        console.error("Start page must be less than or equal to end page")
        return
    }
    if (startPage < 1) {
        console.error("Start page must be greater than or equal to 1")
        return
    }
    if (sleepTimeMs < 500) {
        if (!confirm("Are you sure to set sleep time less than 500ms? It may fail to capture the document content.")) {
            return
        }
    }

    const sleep = async (delayMs) => { await new Promise(resolve => setTimeout(resolve, delayMs)) }

    // WARN: some hardcoded elements may break when sharepoint update in the future
    // start hardcoded elements
    const previousButton = document.getElementsByTagName("button")[7]
    const nextButton = document.getElementsByTagName("button")[8]
    const documentCanvas = document.getElementsByTagName("canvas")[0]
    const getCurrentPage = function () { return document.getElementsByTagName('input')[1].value }
    // resize to page size
    const resize = async () => {
        document.getElementsByTagName("button")[9].click()
        await sleep(sleepTimeMs)
        document.getElementsByTagName("button")[14].click()
    }
    // end of hardcoded elements

    // set up the web to the correct page and page size and temporary block the web interaction
    // show blocker to prevent user from interacting with the web
    const blocker = document.createElement('div');
    blocker.style.position = 'fixed';
    blocker.style.display = 'flex';
    blocker.style.top = '0';
    blocker.style.left = '0';
    blocker.style.width = '100%';
    blocker.style.height = '100%';
    blocker.style.background = 'rgba(255, 255, 255, 0)';
    blocker.style.zIndex = '9999';
    blocker.style.justifyContent = 'center';
    blocker.style.alignItems = 'center';
    const text = document.createElement('div');
    text.textContent = "Capturing content. Do not touch the web or it may fail to fully capture the document."
    text.style.color = 'red';
    text.style.fontSize = '30px';
    text.style.width = '50%';
    blocker.appendChild(text);
    document.body.appendChild(blocker);
    // end: show blocker

    // resize to page size
    await resize()

    // move to correct page
    while (getCurrentPage() != startPage) {
        if (getCurrentPage() > startPage) previousButton.click()
        else nextButton.click()
        await sleep(100)
        console.log("Moving to page: " + getCurrentPage())
    }

    // start download
    // sleep to wait for the canvas to load the first page
    await sleep(sleepTimeMs)
    for (let index = startPage; index <= endPage; index++) {
        const data = documentCanvas.toDataURL('image/png')
        const link = document.createElement("a")
        link.download = basename + "_page_" + index + ".png"
        link.href = data
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        nextButton.click()

        console.log("Capturing page: " + index)

        // sleep to wait for the canvas to load the next page
        // longer result in higher rate in successfully capture full content but slower to download
        await sleep(sleepTimeMs)
    }
    // finish download

    // remove blocker
    document.body.removeChild(blocker);
}

async function test() {
    const sleep = async (delayMs) => { await new Promise(resolve => setTimeout(resolve, delayMs)) }
    const previousButton = document.getElementsByTagName("button")[7]
    const nextButton = document.getElementsByTagName("button")[8]
    const getCurrentPage = function () { return document.getElementsByTagName('input')[1].value }
    const resize = async () => {
        document.getElementsByTagName("button")[9].click()
        await sleep(100)
        document.getElementsByTagName("button")[14].click()
    }

    await sleep(1000)

    console.log("Current page: " + getCurrentPage())

    await sleep(1000)

    console.log("Test resize...")
    await resize()
    await sleep(2000)

    console.log("Pressing previous page...")
    previousButton.click()
    console.log("Current page: " + getCurrentPage())
    await sleep(2000)

    console.log("Pressing next page...")
    nextButton.click()
    console.log("Current page: " + getCurrentPage())

    console.log("Done")
}