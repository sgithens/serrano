require(['design/search', 'design/views', 'design/criterialist'], function(search, views, criterialist) {
   
    $(function() {
        search.init();
        // The view manager needs to know where in the DOM to place certain things
        var rootNode = $("#content"),
            pluginTabs = $('#plugin-tabs'),
            pluginPanel = $('#plugin-panel'),
            pluginTitle = $('#plugin-title'),
            criteriaPanel = $("#user-criteria"),
            pluginStaticContent = $('#plugin-static-content'),
            pluginDynamicContent = $('#plugin-dynamic-content');
            
            
    
        // Create an instance of the viewManager object. Only do this once.
        var viewManager = views.manager(pluginPanel, pluginTitle, pluginTabs, pluginDynamicContent,
            pluginStaticContent);
        
        var criteriaManager = criterialist.Manager(criteriaPanel);
        //            
        rootNode.bind('UpdateQueryEvent', function(evt, criteria_constraint) {
            criteriaPanel.triggerHandler("UpdateQueryEvent", [criteria_constraint]);
        });
        
        // Listen for the user clicking on criteria in the right hand panel
        rootNode.bind("ShowConceptEvent", function(evt){
            
            var target = $(evt.target);
           // console.log(target.attr('data-uri'));
            $.ajax({
                url: target.attr('data-uri'),
                dataType:'json',
                success: function(json) {
                        pluginPanel.fadeIn(100);
                        viewManager.show(json);
                    }
                });
                    
        });

        // TODO change this into a jQuery extension or something..
        (function() {
            var cache = {},
                tools = $('#tools'),
                tools_width = tools.width(),
                left_pad = right_pad = 10,
                ft = 100;
            
            function get(e) {
                if (!cache[e.id]) {
                    // center the menu unless it conflicts with the far right
                    // or left edges
                    var label = $(e),
                        menu = $(label.attr('data-for')),
                        menu_width = menu.outerWidth();
            
                    // absolute midpoint of label
                    var label_abs_mid = label.offset().left + (label.outerWidth() / 2),
                        menu_abs_right = label_abs_mid + (menu_width / 2);
                    
                    // menu overflows right edge of document, default to right edge
                    if (menu_abs_right >= document.width - right_pad) {
                        menu.css('right', right_pad);
                    } else {
                        menu.css('right', document.width - menu_abs_right);
                    }
                    cache[e.id] = [label, menu];
                }
                return cache[e.id];
            };
            
            function hide() {
                for (var e in cache) {
                    cache[e][1].hide();
                    cache[e][0].removeClass('selected');
                }
            };

            tools.delegate('#tools > *', 'click', function(evt) {
                var e = get(this), t = e[0], m = e[1];
                
                if (t.hasClass('selected')) {
                    m.fadeOut(ft);
                    t.removeClass('selected');
                } else {
                    hide();
                    t.addClass('selected');
                    m.fadeIn(ft);
                }
            });            
        })();

        $('[data-model=category]').live('click', function(evt) {
            var target = $(this);
            target.trigger('search_criteria', target.data('name'));
            return false;
        });
    
        $('[data-model=criterion]').live('click', function(evt) {
            evt.preventDefault();
            var target = $(this);
            target.trigger('collapse_search');
            target.trigger('ShowConceptEvent');
        
        });
    });
});
