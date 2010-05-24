// Handles related-objects functionality: lookup link for raw_id_fields
// and Add Another links.

function html_unescape(text) {
    // Unescape a string that was escaped using django.utils.html.escape.
    text = text.replace(/&lt;/g, '<');
    text = text.replace(/&gt;/g, '>');
    text = text.replace(/&quot;/g, '"');
    text = text.replace(/&#39;/g, "'");
    text = text.replace(/&amp;/g, '&');
    return text;
}

function html_escape(text) {
    text = text.replace(/&/g, '&amp;');
    text = text.replace(/</g, '&lt;');
    text = text.replace(/>/g, '&gt;');
    text = text.replace(/"/g, '&quot;');
    text = text.replace(/'/g, '&#39;');
    return text;
}

// IE doesn't accept periods or dashes in the window name, but the element IDs
// we use to generate popup window names may contain them, therefore we map them
// to allowed characters in a reversible way so that we can locate the correct
// element when the popup window is dismissed.
function id_to_windowname(text) {
    text = text.replace(/\./g, '__dot__');
    text = text.replace(/\-/g, '__dash__');
    return text;
}

function windowname_to_id(text) {
    text = text.replace(/__dot__/g, '.');
    text = text.replace(/__dash__/g, '-');
    return text;
}

function getAdminMediaPrefix() {
  if (window.__admin_media_prefix__ != undefined)
    return window.__admin_media_prefix__;

  return '/missing-admin-media-prefix/';
}

var CLEAR_RAW_ID = '<a href="#" onclick="return clearRawId(this);">' +
'<img src="' + getAdminMediaPrefix() + 'img/admin/icon_deletelink.gif" ' +
'width="10" height="10" alt="Clear" title="Clear" /></a>';

// FIXME: the following produce 'gettext is not defined' errors in FireBug.
// Needs to be tracked down.
// (jsi18n is generally included before this in admin templates)
//
// 'width="10" height="10" alt="' + gettext('Clear') + '" title="' +
// gettext('Clear') + '" /></a>';

function showRelatedObjectPopup(triggeringLink) {
    var name = triggeringLink.parentNode.id.replace(/^view_lookup_/, '');
    name = id_to_windowname(name);
    return openPopupWindow(triggeringLink.href, '_popup', name);
}

function showRelatedObjectLookupPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^lookup_/, '');
    name = id_to_windowname(name);
    return openPopupWindow(triggeringLink.href, 'pop', name);
}

function dismissRelatedLookupPopup(win, chosenId, chosenIdHref, chosenName) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    var nameElem = document.getElementById("view_lookup_" + name);

    if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
        elem.value += ',' + chosenId;
    } else {
        document.getElementById(name).value = chosenId;
    }

    if (nameElem) {
      nameElem.innerHTML = '<a href="' + chosenIdHref + '" ' +
       'onclick="return showRelatedObjectPopup(this);">' +
        html_escape(chosenName) + '</a> ' + CLEAR_RAW_ID;
    }

    win.close();
}

function showAddAnotherPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^add_/, '');
    name = id_to_windowname(name);
    return openPopupWindow(triggeringLink.href, '_popup', name);
}

function dismissAddAnotherPopup(win, newId, newRepr) {
    // newId and newRepr are expected to have previously been escaped by
    // django.utils.html.escape.
    newId = html_unescape(newId);
    var newRepr_escaped = newRepr;
    newRepr = html_unescape(newRepr);
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem) {
        if (elem.nodeName == 'SELECT') {
            var o = new Option(newRepr, newId);
            elem.options[elem.options.length] = o;
            o.selected = true;
        } else if (elem.nodeName == 'INPUT') {
            if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
                elem.value += ',' + newId;
            } else {
                elem.value = newId;
            }

            var nameElem = document.getElementById("view_lookup_" + name);
            if (nameElem) {
                var chosenIdHref = win.location.href.replace(/\/add\/[^\/]*$/,
                    '/' + newId + '/');
                nameElem.innerHTML = '<a href="' + chosenIdHref + '" ' +
                  'onclick="return showRelatedObjectPopup(this);">' +
                  newRepr_escaped + '</a> ' + CLEAR_RAW_ID;
            }
        }
    } else {
        var toId = name + "_to";
        elem = document.getElementById(toId);
        var o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    win.close();
}

function clearRawId(triggeringLink) {
    triggeringLink.parentNode.previousSibling.previousSibling.previousSibling.previousSibling.value = '';
    triggeringLink.parentNode.innerHTML = '';
    return false;
}

function openPopupWindow(href, popup_var, name) {
    if (href.indexOf('?') == -1) {
        href += '?';
    } else {
        href  += '&';
    }
    href += popup_var + '=1';
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}
