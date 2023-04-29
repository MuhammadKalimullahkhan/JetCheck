import os


BASE_DIR = os.path.abspath(".")

UPLOAD_DIR = BASE_DIR + "/static/uploads/"
PDF_UPLOAD_DIR = BASE_DIR + "/static/uploads/pdf/"

SUPPORTED_DATE_FORMATES = [
    '%Y-%m-%d', # yyyy-mm-dd
    '%d-%m-%Y', # dd-mm-yyyy
    '%m-%d-%Y', # mm-dd-yyyy
    '%Y/%m/%d', # yyyy/mm/dd
    '%d/%m/%Y', # dd/mm/yyyy
    '%m/%d/%Y', # mm/dd/yyyy
    '%Y.%m.%d', # yyyy.mm.dd
    '%d.%m.%Y', # dd.mm.yyyy
    '%m.%d.%Y', # mm.dd.yyyy
    '%Y_%m_%d', # yyyy_mm_dd
    '%d_%m_%Y', # dd_mm_yyyy
    '%m_%d_%Y', # mm_dd_yyyy
    '%Y%m%d',   # yyyymmdd
    '%d%m%Y',   # ddmmyyyy
    '%m%d%Y',   # mmddyyyy
    '%d-%b-%Y', # dd-MMM-yyyy
    '%d-%b-%y', # dd-MMM-yy
    '%d/%b/%Y', # dd/MMM/yyyy
    '%d.%b.%Y', # dd.MMM.yyyy
    '%d %b %Y', # dd MMM yyyy
    '%d %B %Y', # dd Month yyyy
]

ALLOWED_CONTENT_TYPES = [
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.oasis.opendocument.text',    
    'application/rtf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
    'application/vnd.ms-word.document.macroEnabled.12',
    'application/vnd.ms-word.template.macroEnabled.12',
    'application/vnd.ms-word.document.binary.macroEnabled.12',
    'application/pdf',
    'text/plain'
    'text/html',    
    'application/vnd.google-apps.document',    
    'application/vnd.google-apps.spreadsheet',    
    'application/vnd.google-apps.presentation',
]


ALL_CONTENT_TYPES = [
    'application/atom+xml',
    'application/ecmascript',
    'application/EDI-X12',
    'application/EDIFACT',
    'application/json',
    'application/javascript',
    'application/octet-stream',
    'application/ogg',
    'application/pdf',
    'application/postscript',
    'application/rdf+xml',
    'application/rss+xml',
    'application/soap+xml',
    'application/font-woff',
    'application/xhtml+xml',
    'application/xml-dtd',
    'application/xop+xml',
    'application/zip',
    'application/gzip',
    'application/x-bzip',
    'application/x-bzip2',
    'application/x-rar-compressed',
    'application/x-tar',
    'application/x-7z-compressed',
    'application/x-msdownload',
    'application/x-shockwave-flash',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.oasis.opendocument.text',
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.oasis.opendocument.presentation',
    'application/vnd.mozilla.xul+xml',
    'application/vnd.google-earth.kml+xml',
    'application/vnd.google-earth.kmz',
    'application/vnd.wap.wmlc',
    'application/vnd.wap.wmlscriptc',
    'application/x-dvi',
    'application/x-latex',
    'application/x-font-ttf',
    'application/x-javascript',
    'application/x-mpegurl',
    'application/x-ruby',
    'application/x-sh',
    'application/x-tcl',
    'application/x-tex',
    'application/x-ustar',
    'audio/basic',
    'audio/L24',
    'audio/mp4',
    'audio/mpeg',
    'audio/ogg',
    'audio/vorbis',
    'audio/vnd.rn-realaudio',
    'audio/vnd.wave',
    'audio/webm',
    'image/gif',
    'image/jpeg',
    'image/pjpeg',
    'image/png',
    'image/svg+xml',
    'image/tiff',
    'image/vnd.wap.wbmp',
    'image/webp',
    'image/x-icon',
    'message/rfc822',
    'text/css',
    'text/csv',
    'text/html',
    'text/plain',
    'text/xml',
    'video/3gpp',
    'video/mp4',
    'video/mpeg',
    'video/ogg',
    'video/quicktime',
    'video/vnd.mpegurl',
    'video/x-msvideo',
    'video/x-flv',
    'video/webm',
    'video/x-ms-wmv',
    'application/x-pkcs12',
    'application/x-pkcs7-certificates',
    'application/x-pkcs7-certreqresp',
    'application/x-rar-compressed',
    'application/x-x509-ca-cert',
    'application/x-x509-user-cert',
    'application/x-shockwave-flash',
    'application/x-futuresplash',
    'application/vnd.ms-outlook',
    'application/vnd.ms-cab-compressed',
    'application/x-ms-application',
    'application/x-ms-xbap',
    'application/vnd.ms-xpsdocument',
    'application/vnd.ms-access',
    'application/vnd.ms-project',
    'application/vnd.ms-word.document.macroEnabled.12',
    'application/vnd.ms-excel.sheet'
]
