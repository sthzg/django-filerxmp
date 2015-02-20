/**
 * fxmpadmin is a javascript object that provides functionality used to
 * enhance the admin area.
 *
 * @type {{get_xmpbase_by_fid: get_xmpbase_by_itempk}}
 */

    // Dev-Note
    // --------
    // This is a first step towards the final, ajax'ified version. Later in
    // development it will become a design process to split utilities in this
    // method to two or more objects (fxmpuser, fxmpeditor, fxmpadmin, ...).
    // Only the object up to the current user (or guest's) permission level
    // will be loaded.

var fxmpadmin = {

  data_store: [],

  init: function() {

    var that = this;

    // Enhance the change form for items.
    if ($('body').hasClass('filersets-item', 'change-form')) {
      var $el = $('<div></div>');
      $el.bind('xmpbase_data_ready', function(ev) {
        that.init_copy_from_xmp_title(that.data_store[0]);
        that.init_copy_from_xmp_description(that.data_store[0]);
      });
      this.get_xmpbase_by_filepk($('input.vForeignKeyRawIdAdminField').val(), $el);
    }

    // Enhance the change form for files.
    if ($('body').hasClass('filer-image', 'change-form')) {
      var $el = $('<div></div>');
      $el.bind('xmpbase_data_ready', function(ev) {
        that.init_copy_from_xmp_keywords(that.data_store[0]);
        that.init_copy_from_xmp_title(that.data_store[0]);
        that.init_copy_from_xmp_description(that.data_store[0]);
      });
      this.get_xmpbase_by_filepk($('#id_filemodelext_file-0-filer_file').val(), $el);
    }
  },

  /**
   * Fire the data for one XMPBase item retrieved by fid on $fire_on.
   *
   * @param pk_file
   * @param $fire_on
   */
  get_xmpbase_by_filepk: function(pk_file, $fire_on) {
    $.ajax({
      url: '/api/v1/fxmpimage/'+pk_file+'/',
      context: this,
      success: function(data) {
        this.data_store.push({
          'fid': pk_file,
          'data': data
        });
        $fire_on.trigger('xmpbase_data_ready', data);
      }
    })
  },

  /**
   * Provides a 'Copy from XMP' button to paste in the xmp title.
   *
   * @param data
   */
  init_copy_from_xmp_title: function(data) {
    //                                                                     _____
    //                                                                     Title
    if (data.data.xmp_title.length > 0) {
      var $inp_title = $('input#id_name');
      var $el = $('&nbsp;<span class="inline-link" style="margin-left: 10px;">[ <a href="#">Copy from XMP</a> ]</span>');
      $el.insertAfter($inp_title);
      $el.bind('click', function(ev) {
        $inp_title.val(data.data.xmp_title);
      });
    }
  },

  /**
   * Provides a 'Copy from XMP' button to paste in the xmp description.
   *
   * @param data
   */
  init_copy_from_xmp_description: function(data) {
    //                                                               ___________
    //                                                               Description
    if (data.data.xmp_description.length > 0 ) {
      var $txt_description = $('textarea#id_description');
      var $el = $('&nbsp;<span class="inline-link" style="margin-left: 10px">[ <a href="#">Copy from XMP</a> ]</span>');
      $el.insertAfter($txt_description);
      $el.bind('click', function(ev) {
        $txt_description.val(data.data.xmp_description);
      });
    }
  },

  /**
   * Provides a 'Copy from XMP' button to paste in the xmp keywords.
   *
   * @param data
   */
  init_copy_from_xmp_keywords: function(data) {
    //                                                                      ____
    //                                                                      Tags
    if (data.data.xmp_keywords.length > 0) {
      setTimeout(function() {
        var $inp_tags = $('#s2id_id_filemodelext_file-0-tags__tagautosuggest');
        var $el = $('<span class="inline-link" style="margin-left: 10px;"> [ <a href="#">Copy from XMP</a> ]</span>');
        $el.insertAfter($inp_tags);
        $el.bind('click', function(ev) {
          var tags = data.data.xmp_keywords.join(', ');
          $("#id_filemodelext_file-0-tags").val(tags);
          $("#id_filemodelext_file-0-tags__tagautosuggest").val(tags).trigger('change');
          return false;
        });
      }, 200);
    }
  },

  /**
   * Initializes enhancements for the change form of a single item.
   */
  init_change_form_enhancements: function(data) {
    //                                                                     _____
    //                                                                     Title
    if (data.data.xmp_title.length > 0) {
      var $inp_title = $('input#id_title');
      var $el = $('<span class="inline-link">[<a href="#">Copy from XMP</a>]</span>');
      $el.insertAfter($inp_title);
      $el.bind('click', function(ev) {
        $inp_title.val(data.data.xmp_title);
      });
    }

    //                                                               ___________
    //                                                               Description
    if (data.data.xmp_description.length > 0 ) {
      var $txt_description = $('textarea#id_description');
      var $el = $('<span class="inline-link">[<a href="#">Copy from XMP</a>]</span>');
      $el.insertAfter($txt_description);
      $el.bind('click', function(ev) {
        $txt_description.val(data.data.xmp_description);
      });
    }

    //                                                                      ____
    //                                                                      Tags
    if (data.data.xmp_keywords.length > 0) {
      setTimeout(function() {
        var $inp_tags = $('#s2id_id_tags__tagautosuggest');
        var $el = $('<span class="inline-link">[<a href="#">Copy from XMP</a>]</span>');
        $el.insertAfter($inp_tags);
        $el.bind('click', function(ev) {
          var tags = data.data.xmp_keywords.join(', ');
          $("#id_tags").val(tags);
          $("#id_tags__tagautosuggest").val(tags).trigger('change');
          return false;
        });
      }, 200);
    }
  }
};

$(document).ready(function() {
  fxmpadmin.init();
});


// Get Cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}