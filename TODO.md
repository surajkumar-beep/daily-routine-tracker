# Task Management Feature Plan

**Status: [ ] In Progress**

## Information Gathered:
- tasks.json: `["Wakeup","No Tea or Coffee","Brush","Breakfast","Art","Lunch","Snacks","Watering Plants","Reading Books","Dinner","Sleep"]`
- app.py: loads tasks, displays, updates CSV
- index.html: renders task checkboxes
- CSV headers must sync with tasks.json changes

## Plan:
1. **app.py**: 
   - `/manage` GET: render manage.html with current tasks list
   - `/manage` POST: handle add/delete, rewrite tasks.json
   - Update ensure_csv_header to add new columns as needed
2. **templates/manage.html**: Form with task list (delete buttons), add input + button
3. **index.html**: Add "Manage Tasks" button linking /manage
4. **style.css**: Style manage form matching theme

## Dependent Files:
- app.py (backend routes)
- templates/manage.html (NEW)
- templates/index.html (add link)
- static/style.css (manage styles)
- tasks.json (dynamic)
- routine.csv (header sync)

## Follow-up Steps:
✅ Create manage.html  
✅ Add routes to app.py  
✅ Update index.html link  
✅ Style manage page  
✅ **COMPLETE** - Fully functional task management!

## Progress:
- [x] Dashboard → Manage Tasks button
- [x] Add new tasks (updates tasks.json + CSV column)
- [x] Delete tasks (updates tasks.json + drops CSV column)  
- [x] Auto-save on add/delete
- [x] Glassmorphism styling matching theme
- [x] Responsive design

**Feature Complete!** 🚀

