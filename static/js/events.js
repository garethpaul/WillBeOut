var currentTime = new Date()
var m = currentTime.getMonth() + 1;
var month = '';
if (m < 10) {
	month = '0' + m;
} else {
	month = m;
}
var d = currentTime.getDate();
day = ''
if (d < 10) {
	day = '0' + d;
} else {
	day = d;
}
var year = currentTime.getFullYear();

// MONTH FUNCTION


function getMonth(m) {
	if (m < 10) {
		month = '0' + m;
		return month
	} else {
		return m
	}
}

$('#from').attr('data-date', year + '-' + month + '-' + day);
$('#to').attr('data-date', year + '-' + month + '-' + day);
$('.to').attr('value', year + '-' + month + '-' + day);
$('.from').attr('value', year + '-' + month + '-' + day);
$('.date').datepicker();
var startDate = new Date(2012, 08, 26);
var endDate = new Date(2012, 08, 27);
$('#to').datepicker().on('changeDate', function(ev) {
	$('#alert').hide();
	console.log(ev.date.valueOf());
	if (ev.date.valueOf() < endDate.valueOf()) {
		endDate = new Date(ev.date);
		$('#alert').html('The end date cannot be before the start date');
		$('#alert').show();
	}
});
$('#from').datepicker().on('changeDate', function(ev) {
	console.log(ev.date.valueOf());
	$('#alert').hide();
	$('.to').val($('.from').val());
	$('#to').attr('data-date', $('.from').val());
	if (ev.date.valueOf() > startDate.valueOf()) {
		startDate = new Date(ev.date);
		$('#alert').html('The end date cannot be before the start date');
		$('#alert').show();
	}
});

$('#from').attr('data-date', year + '-' + month + '-' + day);
$('#to').attr('data-date', year + '-' + month + '-' + day);
$('.to').attr('value', year + '-' + month + '-' + day);
$('.from').attr('value', year + '-' + month + '-' + day);
$('.date').datepicker();

function addOverlay() {
	$.each(e.event, function(k, v) {
		var m = parseInt(v.date.split('-')[1]);
		if (v.date.split('-')[1] < 10) {
			m = String(v.date.split('-')[1]).replace('0', '');
		}
		console.log(m);
		var y = String(parseInt(v.date.split('-')[0]));
		var d = String(parseInt(v.date.split('-')[2]));
		a = '[day="' + d + '"]' + '[month="' + m + '"]' + '[year="' + y + '"]';
			$(a).css('background', 'red');
		$(a).css('opacity', '0.5');
		$(a).css('color', 'white');
	});
}

$('#calendar').Calendar({
	'weekStart': 1
});


function getData(dos) {
	//console.log(dos);
	html = '<ul id="info_events">';
	html += '<li><h2>' + 'Events' + '</h2></li>';
	$.each(e.event, function(k, v) {
		if (dos == v.date) {
			html += '<li><a href="/event?event_id=' + v.id + '">' + v.place + '</a> - </li>';
		}
	});
	html += '</ul>'
	return html;
}

function checkInfos() {
	var a = $('#info_events').find('li');
	if (a.length >= 1) {
		$('#info_events').prepend('<li>Events</li>')
	}
	$('#calendar-info .page-header').show();
}

// document ready 
$(document).ready(function() {
	//
	var currentTime = new Date();
	string = currentTime.getFullYear() + '-' + getMonth(currentTime.getMonth()+1) + '-' + getMonth(currentTime.getDate());
	$('#calendar-info .head').show();
	html = '<h2>' + string + '</h2>';
	$('#calendar-info .detail').html(getData(string));
	$('#info_events li:first-child').css('padding-top', '0px');
	$('#info_events li a').css('font-size','2em');
	$('.nevent').attr('data-date', string);
	//console.log(string);
});

function letsGo() {
	$('.day').click(function() {
		$('#calendar-info .detail').html('')
		var d = $(this).attr('day');
		var m = $(this).attr('month');
		var y = $(this).attr('year');
		$('#calendar-info .head').show();
		html = '<h2>' + getMonth(y) + '-' + getMonth(m) + '-' + getMonth(d);
		$('.nevent').attr('data-date', y + '-' + getMonth(m) + '-' + getMonth(d));
		$('#calendar-info .detail').html(html + getData(getMonth(y) + '-' + getMonth(m) + '-' + getMonth(d))).show();
		checkInfos();
	});

	$('.weekend').click(function() {
		$('#calendar-info .detail').html('')
		var d = $(this).attr('day');
		var m = $(this).attr('month');
		var y = $(this).attr('year');
		$('#calendar-info .head').show();
		html = '<h2>' + getMonth(y) + '-' + getMonth(m) + '-' + getMonth(d);
		$('.nevent').attr('data-date', y + '-' + getMonth(m) + '-' + getMonth(d));
		$('#calendar-info .detail').html(html + getData(getMonth(y) + '-' + getMonth(m) + '-' + getMonth(d))).show();
	});
	$('.nevent').click(function() {
		var d = $(this).attr('data-date');
		$('#newform #from').attr('data-date', d);
		$('#newform #to').attr('data-date', d);
		$('#newform .to').attr('value', d);
		$('#newform .from').attr('value', d);
		checkInfos();
	});
}
letsGo();
setTimeout(function() {
	addOverlay()
}, 1000); // delays 1.5 sec
$('.arrow').click(function() {
	setTimeout(function() {
		addOverlay()
	}, 1000); // delays 1.5 sec
	setTimeout(function() {
		letsGo()
	}, 1000);
});


var js_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
var today = new Date();
var w2date = function(year, wn, dayNb) {
		var j10 = new Date(year, 0, 10, 12, 0, 0),
			j4 = new Date(year, 0, 4, 12, 0, 0),
			mon1 = j4.getTime() - j10.getDay() * 86400000;
		return new Date(mon1 + ((wn - 1) * 7 + dayNb) * 86400000);
	};
var week = today.getWeek();

$('.data').attr('data-weekno', week);
var month = today.getMonth();
var year = today.getFullYear();
var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
var times = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
table = $('.weekly tbody');

// write out the table headers
th = '<tr>'
th += '<th width="6%">&nbsp;</th>'

$.each(days, function(ia, day) {
	var _date = w2date(year, week, ia).getDate();
	var _month = w2date(year, week, ia).getMonth() + 1;
	th += '<th width="12%">' + day + ' ' + _month + '/' + _date + '</th>';
});
th += '</tr>';
$($('.weekly thead')[0]).append(th);

$.each(times, function(i, v) {
	var tr = '<tr data-rowid="' + v + '00">';
	//console.log(v);	
	tr += '<td data-time="' + v + '">' + v + ':00 </td>';
	$.each(days, function(ia, day) {
		var _date = w2date(year, week, ia).getDate();
		var _month = w2date(year, week, ia).getMonth() + 1;
		var _year = w2date(year, week, ia).getFullYear();
		tr += '<td data-time="' + v + '" data-month="' + _month + '" data-date="' + _date + '" data-day="' + day + '" data-year="' + _year + '"></td>';
	});
	tr += '</tr>'

	tr += '<td data-time="' + v + '">' + v + ':30 </td>';
	$.each(days, function(ia, day) {
		var _date = w2date(year, week, ia).getDate();
		var _month = w2date(year, week, ia).getMonth() + 1;
		var _year = w2date(year, week, ia).getFullYear();
		tr += '<td data-time="' + v + .5 + '" data-month="' + _month + '" data-date="' + _date + '" data-day="' + day + '" data-year="' + _year + '"></td>';
	});
	tr += '</tr>'

	$('.weekly tbody').append(tr);

});

function checkDataAdded() {
	$('.true').hover(function() {
		a = $(this).length
		$(this).append('<span class="icon icon-remove pull-right"></span>');
		$(this).find('span').click(function() {
			//sdasdsa
			b = $(this).parent();
			console.log({
				'day': b.attr('data-day'),
				'hour': b.attr('data-time'),
				'month': b.attr('data-month'),
				'date': b.attr('data-date')
			});
		});

	}, function() {
		$(this).find('span').remove();
	});
}
// START THE IMPORT
$.getJSON('/calendar/get?wk=' + week, function(data) {
	$.each(data, function(key, value) {
		$('.weekly').find('[data-day="' + value.day + '"][data-time="' + getMonth(value.hour) + '"]').html('<div>' + value.string + '</div>').addClass('true');
	});
	checkDataAdded();
});

function getList(time, day, text) {
	var tdtime = $('.weekly tbody tr td [data-time="' + time + '"][data-day="' + day + '"]');
	tdtime.css('background', 'red');
}
$('.weekly tbody tr td').css('font-size', '11px');
$('.weekly').css({
	'height': '500px',
	'min-height': '500px'
});
$('.weekly tbody tr td').toggle(function() {
	$('.weekly tbody tr td').popover('destroy');
	$('.weekly tbody tr td').css('background', 'white');
	$('[data-detail="true"]').attr('data-detail', 'prev');
	$('.weekly tbody tr td :not[data-detail="false"]').attr('rowspan', '1');
	day = $(this).attr('data-day');
	hour = $(this).attr('data-time')
	a = $(this).parent().next().attr('data-rowid');
	b = $('[data-rowid="' + a + '"] [data-day="' + day + '"]');
	b.css({
		'background': 'red'
	});
	$.each($('.weekly tbody tr td'), function(i, v) {
		//
	});
	$(this).css('background', 'red');
	$(this).popover({
		trigger: 'manual',
		animate: false,
		placement: 'top',
		offset: 5,
		html: true,
		title: 'Create Event <span class="icon icon-remove rmpop pull-right"></span>',
		content: '<input style="width:200px" type="text" name="e_name" /><button class="btn nevent ne">Submit</button>'
	});

	$(this).popover('show');
	$(this).attr('data-detail', 'true');
	$('.rmpop').click(function() {
		console.log('clock');
		$('.popover').remove();
		// _hour
		// _day = day
		// _week
		// _month
		// _string
		$('.weekly td').attr('data-detail', 'false');
		$('.weekly tbody tr td').css('background', 'white');
	});

	$('.ne').click(function() {
		n = $('[name="e_name"]').val();
		$('[data-detail="true"]').html('<div>' + n + '</div>').attr('rowspan', '1');
		d = $('[data-detail="true"]');
		_day = $('[data-detail="true"]').attr('data-day');
		_date = $('[data-detail="true"]').attr('data-date');
		_week = $('.data').attr('data-weekno');
		_hour = $('[data-detail="true"]').attr('data-time');
		_month = $('[data-detail="true"]').attr('data-month');
		_year = $('[data-detail="true"]').attr('data-year');
		_string = n;
		$.post("/calendar/post", {
			string: _string,
			day: _day,
			d: _date,
			week: _week,
			hour: _hour,
			month: _month,
			year: _year
		});
		d2 = $('[data-detail="true"]').parent().next().find('td').filter('[data-day="' + d + '"]')[0];
		$(d2).css('border-top', 'red');
		$('[data-detail="true"]').attr('data-added', 'true');
		$('[data-detail="true"]').attr('data-detail', 'false');
		$('.popover').remove();
	});
}, function() {

});
